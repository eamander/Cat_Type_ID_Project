import pandas as pd
import numpy as np
import os
import shutil
from keras.backend import floatx


def label_maker(dframe, target_dir, source_dir=None, data_col=None, label_cols=None, train=0.8, test=0.1, val=0.1,
                delete_old_files=False, sym_links=False, hierarchy='flat'):
    """
    Given a DataFrame, source directory, and a target directory, creates folders for each
    label combination in the DataFrame and copies each .jpg into its respective folder

    :param pandas.DataFrame dframe:
    :param str target_dir:
                 Destination directory for the hierarchy of folders specifying the image labels
    :param str | NoneType source_dir:
        [None] - if not None, the file names (located in the column indicated by data_col)
                 are presumed to all reside within the source dir
                 Otherwise, the file names are presumed to be the path
    :param str | NoneType data_col:
        [None] - if not None, the column label containing the name or location of each image
                 Otherwise, data_col = 'file_name', or dframe.index if no such column exists
    :param list[str] label_cols:
        [None] - if not None, a list of the dframe columns associated with each label category.
                 Otherwise, label_cols = dframe.columns[1:]
    :param float train:
        [0.8]  - Fraction (out of 1.0) of images to store as part of the training set
    :param float test:
        [0.1]  - Fraction (out of 1.0) of images to store as part of the test set
    :param float val:
        [0.1]  - Fraction (out of 1.0) of images to store as part of the validation set
    :param bool delete_old_files:
        [False] - While false, adds all images in the input dframe regardless of presence, and starts
                    the file numbering index at 1+ the highest number in the existing target directory.
                  When set to True, removes any existing images in the folder hierarchy
    :param bool sym_links:
        [False] - When set to True, creates symbolic links to the images rather than copying them
    :param str hierarchy:
        ['flat']-Options include:
                   flat: all labels in one folder, multilabel files placed in multiple folders
                   deep: each value in label_col describes a new depth in the tree.
                   each value in label_col_lists describes the number of branches at the given depth
                   none: make the target_dir only, if it does not exist.

    :return str target_dir:
    :return str label_cols:
    :return pandas.DataFrame new_dframe:

    """

    dframe = dframe.copy()

    hierarchy = hierarchy.lower()

    if int(train + test + val) != 1:
        raise ValueError("train + test + val must sum to 1")

    # Actually let's not index by file name
    # because we might have to change all these names
    if data_col is None:
        data_col = 'file_name'
        if 'file_name' in dframe.columns:
            dframe.reset_index(inplace=True, drop=True)
        else:
            # This lets us use the same formulation for the rest of the function
            # by renaming the index and moving it into the columns
            dframe.index.rename(data_col, inplace=True)
            dframe.reset_index(inplace=True)

    # Rewrite a bunch of file names if you have to:
    if source_dir:
        dframe[data_col] = dframe[data_col].apply(lambda fname: os.path.join(source_dir, fname))

    # data_list = dframe.index.tolist()  # we don't need this, we can use iloc

    if label_cols is None:
        # This helps us normalize the organization of the folders.
        label_cols = dframe.columns.sort_values().tolist()
        label_cols.remove(data_col)
        label_cols.sort()

    # store a list-like object referencing the labels for each category
    label_col_lists = [sorted(dframe[category].unique().tolist()) for category in label_cols]

    '''
    Some notes on what I want to do:
    [x] 1. Make a hierarchy of folders at the target_dir representing the labels 
    [x] 2. Copy the images from the data directory to their respective label location
    
    use label_cols, which is sorted, to figure out the folder hierarchy. It will be:
    label_cols[0]\\label_cols[1]\\etc.
    '''
    # make the hierarchy of folders:
    # This may be a lot of folders.
    for i in ['train', 'validation', 'test']:
        dir_maker(target_dir=os.path.join(target_dir, i),
                  label_cols=label_cols,
                  label_col_lists=label_col_lists,
                  delete_old_files=delete_old_files,
                  hierarchy=hierarchy)

    rand_arr = np.random.random((len(dframe),))

    # Now copy images to the new folders. This does not move the old images
    new_dframe = dframe.copy()

    # if we are picking up where we left off, find the starting index.
    if not delete_old_files:
        dirs = [os.path.join(target_dir, dir) for dir in ['train', 'validation', 'test']]
        start_index = [[].extend(os.listdir(path)) for path in dirs][0]
        start_index = max([int(name.split('_')[1].split('.')[0]) for name in start_index]) + 1
    else:
        start_index = 0
    for j in range(len(dframe)):
        i = j + start_index
        rand = rand_arr[i]
        row = dframe.iloc[i]
        src = row[data_col]
        if rand <= train:
            dst = os.path.join(target_dir, 'train')
        elif rand <= (train + test):
            dst = os.path.join(target_dir, 'test')
        else:
            dst = os.path.join(target_dir, 'validation')

        # join_list = []
        if hierarchy == 'flat':
            for col in label_cols:
                end_path = os.path.join(row[col], 'cat_{}.jpg'.format(i))
                # join_list.append(row[col])

                # join_list.append('cat_{}.jpg'.format(i))

                new_dst = os.path.join(dst, end_path)  # *join_list)
                if not os.path.isfile(new_dst):
                    if not sym_links:
                        shutil.copy(src, new_dst)
                    else:
                        os.symlink(src, new_dst)
        elif hierarchy == 'none':
            end_path = 'cat_{}.jpg'.format(i)
            new_dst = os.path.join(dst, end_path)
            if not os.path.isfile(new_dst):
                if not sym_links:
                    shutil.copy(src, new_dst)
                else:
                    os.symlink(src, new_dst)
        elif hierarchy == 'deep':
            join_list = []
            for col in label_cols:
                join_list.append(row[col])

            join_list.append('cat_{}.jpg'.format(i))
            end_path = os.path.join(*join_list)
            new_dst = os.path.join(dst, end_path)
            if not os.path.isfile(new_dst):
                if not sym_links:
                    shutil.copy(src, new_dst)
                else:
                    os.symlink(src, new_dst)
        else:
            raise ValueError("Bad value passed to argument 'hierarchy': {}. Use 'flat', 'deep', or 'none' instead.")
        new_dframe.loc[i, data_col] = end_path

    # Find the files referenced in the dataframe and copy them to their new homes!
    return target_dir, label_cols, new_dframe


def dir_maker(target_dir, label_cols=[], label_col_lists=[], delete_old_files=False, hierarchy='flat'):
    """
    Under Construction
    This makes a set of directories based on labels in DataFrame columns.

    Issues:
    Multilabel solutions don't currently work correctly because Keras does not have k-hot vector encoding for
    the flow_from_directory method.
    flow_from_directory considers the same file / symbolic link in different directories to be different files.

    :param target_dir:
    :param label_cols:
    :param label_col_lists:
    :param delete_old_files:
        [False]         - if True, deletes all .jpg files in the subdirectories listed in label_cols
                          for safety, this is not implemented for hierarchy='none'
    :param str hierarchy:
        ['flat']        - Options include:
                            flat: all labels in one folder, multilabel files placed in multiple folders
                            deep: each value in label_col describes a new depth in the tree.
                                  each value in label_col_lists describes the number of branches at the given depth
                            none: make the target_dir only, if it does not exist.

    :return None:
    """
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    hierarchy = hierarchy.lower()

    if hierarchy == 'none':
        return None
    elif hierarchy == 'flat':
        for category in label_col_lists:
            for label in category:
                if not os.path.exists(os.path.join(target_dir, label)):
                    os.mkdir(os.path.join(target_dir, label))
                if delete_old_files:
                    list_of_files = [os.path.join(target_dir, label)
                                     for file in os.listdir(target_dir) if file[-4:] == ".jpg"]
                    for f in list_of_files:
                        os.unlink(f)
    elif hierarchy == 'deep':
        if label_col_lists:
            for label_dir in label_col_lists[0]:
                dir_maker(os.path.join(target_dir, label_dir), label_cols[1:], label_col_lists[1:], hierarchy=hierarchy)
            return None  # If we end up here, we are not at the bottom of the tree
        elif delete_old_files:
            list_of_files = [os.path.join(target_dir, file) for file in os.listdir(target_dir) if file[-4:] == ".jpg"]
            for f in list_of_files:
                os.unlink(f)
    else:
        raise ValueError("Bad value passed to argument 'hierarchy': {}. Use 'flat', 'deep', or 'none' instead.")

    return None


# Build k-hot categorical vector dictionary from dataframe
def k_hot_dict_maker(dframe, data_col=None, label_cols=None, separate_vectors=False, uniqueify=True, inplace=True):
    # Avoid modifying the original data frame
    if not inplace:
        dframe = dframe.copy()
    if data_col is None:
        data_col = 'file_name'
        if 'file_name' in dframe.columns:
            pass
        else:
            # This lets us use the same formulation for the rest of the function
            dframe.index.rename(data_col, inplace=True)
            dframe.reset_index(inplace=True)

    if label_cols is None:
        label_cols = dframe.columns.sort_values().tolist()
        label_cols.remove(data_col)
        label_cols.sort()

    # push the file_names, which are unique, into the index

    dframe = dframe.set_index(data_col)

    if uniqueify:
        for col in label_cols:
            dframe[col] = dframe[col].apply(lambda s: col + '_' + s)

    # store a list-like object containing all unique labels for each category
    # This is where we might want to split this into multiple columns,
    # Or store information about their separation
    labels_arr = np.empty((0,))
    if separate_vectors:
        indiv_label_count_list = []
        # Also, in case labels are shared between frames, append col names to each label
        for col in label_cols:
            dframe[col] = dframe[col].apply(lambda x: col + "_" + x)
    for col in label_cols:
        labels = dframe[col].unique()
        labels_arr = np.append(labels_arr, labels)
        if separate_vectors:
            indiv_label_count_list.append(len(labels))

    labels_arr = pd.Series(labels_arr).unique()
    labels_arr.sort()

    label_count = len(labels_arr)

    label_dict = {}
    for fpath in dframe.index:
        vect = np.zeros((label_count,), dtype=floatx())
        label_list = dframe.loc[fpath].tolist()
        vect[labels_arr.searchsorted(label_list)] += 1
        if separate_vectors:
            ind = 0
            vect_tmp = []
            for i in indiv_label_count_list:
                vect_tmp.append(vect[ind:ind + i])
                ind += i  # increment by count of labels in each col
            vect = vect_tmp

        label_dict[fpath] = vect

    return label_dict


# Build decorator for DirectoryIterator._get_batches_of_transformed_samples(self, index_array)
# I actually have to decorate ImageDataGenerator.flow_from_directory, which returns a DirectoryIterator.
# This is not a big change. Just return a DirectoryIterator with its ._get_batches_of_transformed_samples
# method modified
def multilabel_decorator(func, label_dict):
    # Catch the DirectoryIterator returned by func:
    def inner1(*args, **kwargs):
        dir_iter = func(*args, **kwargs)

        old_batch_getter = dir_iter._get_batches_of_transformed_samples

        # Modify dir_iter's method using our label_dict
        def inner(index_array):
            func_return = old_batch_getter(index_array)
            # Build the return array by collecting all of the k-hot encoded vectors from the dict
            if isinstance(func_return, tuple):
                batch_x = func_return[0]
            else:
                batch_x = func_return
            batch_y = np.zeros((len(batch_x), dir_iter.num_classes), dtype=floatx())
            for i, j in enumerate(index_array):
                batch_y[i] = label_dict[dir_iter.filenames[j]]

            return batch_x, batch_y

        dir_iter._get_batches_of_transformed_samples = inner

        # Return dir_iter, just as before
        return dir_iter

    return inner1


def refactor_str_column(df, str1, str2, col='file_name', inplace=False):
    """
    Takes a column in a dataframe and replaces all instances of str1 with str2

    :param pandas.DataFrame df:
    :param str col:
    :param str str1:
    :param str str2:
    :param bool inplace:
        [False]  - If True, perform the action in-place
                   Note that if this is False, it returns a Series


    :return:

    """
    str1 = str1.replace('\\', '\\\\')
    str2 = str2.replace('\\', '\\\\')

    return df[col].replace(str1, value=str2, regex=True, inplace=inplace)


def rebase_filesystem(df, str1, str2, sep1='\\', sep2='\\', col='file_name', inplace=False):
    """
    refactor path names from one filesystem to another. All instances of
    str1 are replaced with str2. sep1 is the separator used in the filesystem
    of str1, and sep2 the separator for the filesystem of str2.

    :param pandas.DataFrame df:
    :param str str1:
    :param str str2:
    :param str sep1:
    :param str sep2:
    :param str col:
    :param bool inplace:


    :return:
    """

    if not inplace:
        df = df.copy()

    sep1 = sep1.replace('\\', '\\\\')
    sep2 = sep2.replace('\\', '\\\\')

    refactor_str_column(df, str1, str2, col, inplace=True)
    if sep1 != sep2:
        df[col].replace(sep1, value=sep2, regex=True, inplace=True)
    df[col] = df[col].apply(os.path.normpath)

    return df


def key_cleaner(df, key_values):
    comparators = [df[key] != value for key, value in key_values.items()]
    return df[(sum(comparators)).apply(bool)]





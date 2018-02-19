import pandas as pd
import numpy as np
import os
import shutil
from sys import platform
# if platform == 'win32':
#     import win32file


def label_maker(dframe, target_dir, source_dir=None, data_col=None, label_cols=None, train=0.8, test=0.1, val=0.1,
                delete_old_files=False, sym_links=False):
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
        [False] - When set to True, removes any existing images in the folder hierarchy
    :param bool sym_links:
        CURRENTLY ONLY IMPLEMENTED IN WINDOWSw
        [False] - When set to True, creates symbolic links to the images rather than copying them

    :return str target_dir:
    :return str label_cols:

    """

    if platform != 'win32':
        sym_links = False

    dframe = dframe.copy()

    if int(train + test + val) != 1:
        raise ValueError("train + test + val must sum to 1")

    # Actually let's not index by file name
    # because we might have to change all these names
    if data_col is None:
        data_col = 'file_name'
        if 'file_name' in dframe.columns:
            pass
        else:
            # This lets us use the same formulation for the rest of the function
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
                  delete_old_files=delete_old_files)

    rand_arr = np.random.random((len(dframe),))

    # Now copy images to the new folders. This does not move the old images
    for i in range(len(dframe)):
        rand = rand_arr[i]
        row = dframe.iloc[i]
        src = row[data_col]
        if rand <= train:
            dst = os.path.join(target_dir, 'train')
        elif rand <= (train + test):
            dst = os.path.join(target_dir, 'test')
        else:
            dst = os.path.join(target_dir, 'validation')

        join_list = []
        for col in label_cols:
            join_list.append(row[col])

        join_list.append('cat_{}.jpg'.format(i))

        dst = os.path.join(dst, *join_list)
        if not os.path.isfile(dst):
            if not sym_links:
                shutil.copy(src, dst)
            else:
                os.symlink(src, dst)
                # win32file.CreateSymbolicLink(dst, src, 1)
                # The arguments for the above are opposite shutil.copy on purpose

    # Find the files referenced in the dataframe and copy them to their new homes!

    return target_dir, label_cols


def dir_maker(target_dir, label_cols=[], label_col_lists=[], delete_old_files=False):

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if label_col_lists:
        for label_dir in label_col_lists[0]:
            dir_maker(os.path.join(target_dir, label_dir), label_cols[1:], label_col_lists[1:])
        return None  # If we end up here, we are not at the bottom of the tree
    elif delete_old_files:
        list_of_files = [os.path.join(target_dir, file) for file in os.listdir(target_dir) if file[-4:] == ".jpg"]
        for f in list_of_files:
            os.unlink(f)

    return None

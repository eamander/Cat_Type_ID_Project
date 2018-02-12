import pandas as pd
import numpy as np
import os
import shutil


def label_maker(dframe, target_dir, source_dir=None, data_col=None, label_cols=None, train=0.8, test=0.1, val=0.1):
    """
    Given a DataFrame, source directory, and a target directory, creates folders for each
    label combination in the DataFrame and copies each .jpg into its respective folder

    :param dframe: pandas.DataFrame
    :param target_dir: str
    :param source_dir: str
        [None] - if not None, the file names are presumed to all reside within the source dir
                 Otherwise, the file names are presumed to be the source dir
    :param data_col: str
        [None] - if not None, the column label containing the name or location of each image
                 Otherwise, data_col = 'file_name', or dframe.index if no such column exists
    :param label_cols: list
        [None] - if not None, a list of the dframe columns associated with each label category.
                 Otherwise, label_cols = dframe.columns[1:]
    :param train: float
    :param test: float
    :param val: float

    :return:

    """
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
    [ ] 2. Copy the images from the data directory to their respective label location
    
    use label_cols, which is sorted, to figure out the folder hierarchy. It will be:
    label_cols[0]\\label_cols[1]\\etc.
    '''
    # make the hierarchy of folders:
    # This may be a lot of folders.
    for i in ['train', 'validation', 'test']:
        dir_maker(target_dir=os.path.join(target_dir, i),
                  label_cols=label_cols,
                  label_col_lists=label_col_lists)

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
        shutil.copy(src, dst)

    # Find the files referenced in the dataframe and copy them to their new homes!

    return target_dir, label_cols


def dir_maker(target_dir, label_cols=[], label_col_lists=[]):

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if label_col_lists:
        for label_dir in label_col_lists[0]:
            dir_maker(os.path.join(target_dir, label_dir), label_cols[1:], label_col_lists[1:])

    return None


"""
bad_entry_remover.py

This is for removing lines in the dataframe that correspond to a code indicating a bad entry in th data
"""

import pandas as pd
from time import gmtime, strftime
import os


def bad_cat_entry_remover(dframe, reset_index=True, save_copy=True, save_loc=None, save_name='df_copy_'):

    if save_copy:
        if save_loc is None:
            save_loc = os.curdir()
        save_name = save_name + strftime("%Y.%m.%d.%H.%M.%S.df", gmtime())
        dframe.to_pickle(os.path.join(save_loc, save_name))
    if reset_index:
        dframe = dframe.reset_index(drop=True)
    bad_indices = dframe[(dframe.breed == 'Abyssinian') & (dframe.primary_color == 'White')].index
    dframe.drop(bad_indices, inplace=True)

    return dframe


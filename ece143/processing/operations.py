import os
import pandas as pd


def count(df, key, new_count_key):
    """
    This function takes a pandas DataFrame as an input, count the values in the given key column and return a new
    DataFrame with the value as the axis and the new_count_key as the count column name.
    @param df: input DataFrame
    @type df: pd.DataFrame
    @param key: input key by which we will count the values
    @type key: str
    @param new_count_key: column name for the new count column
    @type new_count_key: str
    @return: the new value-count dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(key, str)
    assert isinstance(new_count_key, str)
    assert key in df.columns

    df_counts = df[key].value_counts().rename_axis(key).reset_index(name=new_count_key)
    return df_counts


def aggregate(df, group_key, agg_key):
    """
    This function takes a dataFrame and aggregates the sum value by the given group_key and agg_key.
    @param df: input DataFrame
    @type df: pd.DataFrame
    @param group_key: input key by which we will group the data.
    @type group_key: str
    @param agg_item: the agg key with which we will aggregate the values.
    @type agg_item: str
    @return: new aggregate dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(group_key, str)
    assert isinstance(agg_key, str)
    assert {group_key, agg_key}.issubset(df.columns)

    df_agg = df.groupby([group_key]) \
                       .agg({agg_key:sum}) \
                       .rename_axis(group_key) \
                       .reset_index()
    return df_agg


def merge(df1, df2, key_left, key_right):
    """
    This function takes two dataframes and merges them by the given keys.
    @param df1: input DataFrame 1
    @type df1: pd.DataFrame
    @param df2: input DataFrame 2
    @type df2: pd.DataFrame
    @param key_left: merge key in the first dataFrame
    @type key_left: str
    @param key_right:  merge key in the second dataFrame
    @type key_right: str
    @return: the merged dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df1, pd.DataFrame)
    assert isinstance(df2, pd.DataFrame)
    assert isinstance(key_left, str)
    assert isinstance(key_right, str)
    assert key_left in df1.columns
    assert key_right in df2.columns

    df_merge = pd.merge(df1,
                         df2,
                         left_on=key_left,
                         right_on=key_right,
                         how='right')
    return df_merge


def average(df, key1, key2):
    """
    This function calculates the average value by dividing key1 with key 2.
    @param df: input DataFrame
    @type df: pd.DataFrame
    @param key1: input key that is divided
    @type key1:  str
    @param key2: input key that divides the other column
    @type key2: str
    @return: the original dataFrame with updated key1
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(key1, str)
    assert isinstance(key2, str)

    df[key1] /= df[key2]
    return df


def read_csv_file(csv_file):
    """
    This function uniforms the read csv file as a common function to make the code cleaner and easy to the future
    maintenance.
    :param csv_file: input csv file path
    :type csv_file: str
    :return: pd.DataFrame
    """
    assert isinstance(csv_file, str)
    assert csv_file.endswith(".csv")
    assert os.path.isfile(csv_file), "ERROR! The csv file does not exist"

    return pd.read_csv(csv_file)

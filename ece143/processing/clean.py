import pandas as pd
import processing.constants as constants
from processing.airport import extract_us_airport


def clean_airport_data():
    """
    This function cleans the original worldwide airport data by removing the NA and outlier data. Then it stores the
    cleaned airport data as a csv file.
    """
    original_airports = pd.read_csv(constants.AIRPORT_DATA_PATH)
    cleaned_us_airports = extract_us_airport(original_airports)
    cleaned_us_airports.to_csv(constants.CLEANED_AIRPORT_DATA_PATH)

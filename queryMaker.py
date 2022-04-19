from datetime import datetime, timedelta
import logging
import requests
import sys
import time
import yaml


log_file_name_prefix = datetime.strftime(datetime.now() , "%d-%m-%Y_%H-%M")
logging_formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(module)s:%(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setFormatter(logging_formatter)
logger.addHandler(handler_stdout)

handler_to_file = logging.FileHandler(log_file_name_prefix + "_querryMaker.log", encoding="utf-8")
handler_to_file.setFormatter(logging_formatter)
logger.addHandler(handler_to_file)


def main(start_date, end_date, prod_name, prod_amount, furl, result_file_name, desired_weekday=None, days_per_period=1, date_fmt= "%d-%m-%Y"):

    start = datetime.strptime(start_date, date_fmt)
    end = datetime.strptime(end_date,date_fmt)
    
    if(desired_weekday != None):
        start, end = adjustRangeBounds(start, end, desired_weekday)

    dates_array = generateFormatedDates(start, end)
    prices_array = getPricesAndCalcVal(dates_array, furl, prod_name, prod_amount)

    val_sum = 0
    with open(result_file_name, "a") as f:
        f.write("date, priceUSD, valueUSD\n")
        write_fmt = "{}, {}, {}"
        for tup in prices_array:
            val_sum += tup[2]
            f.write(write_fmt.format(tup[0], tup[1], tup[2])+"\n")
        f.write("#sum: {}USD".format(val_sum)) # use islice or regular reader to read file

# should separate start date and end date adjustments to make tests clearer
def adjustRangeBounds(start_date, end_date, weekday):
    """
    Checks if start and end dates are desired weekday. If not then they are set to 
    the first and last occurence of desired weekday, respectively, within the time period.
    """
    result_start = start_date
    result_end = end_date

    start_day_diff = start_date.weekday() - weekday
    logger.debug("Start date's weekday is "+ str(start_day_diff) +" from desired weekday")

    if(start_day_diff > 0):
        result_start = start_date + timedelta(days = 7-start_day_diff)

    elif (start_day_diff < 0):
        result_start = start_date + timedelta(days = abs(start_day_diff))

    logger.debug("Changed start_date: "+ prettyDate(start_date)+" -> "+ prettyDate(result_start))

    end_day_diff =  end_date.weekday() - weekday
    logger.debug("End date's weekday is "+ str(end_day_diff) +" from desired weekday")
    
    if(end_day_diff > 0):
        result_end = end_date - timedelta(days = end_day_diff)

    elif (end_day_diff < 0):
        result_end = end_date - timedelta(days = 7 - weekday + end_date.weekday())
    
    logger.debug("Changed end_date: "+ prettyDate(end_date)+" -> "+ prettyDate(result_end))

    return (result_start, result_end)


# could use Templates for clearer formatting but more overhead
def getPricesAndCalcVal(array_of_formatted_dates, furl, prod_name, prod_amount):
    """
    fetch prices from API and calculate value. 2-in-1 for code length.

    :param array_of_formatted_dates: Array of dates strings
    :param furl:                  API url string that will be formatted with 
                                    the date strings
    :param prod_name:              Name of product to fetch price data for
    :param prod_amount:            Quantity to calculate the value for each date
    :return:                      list of tuples containing the date, price, and 
                                    value for each date string
    """
    result_list = []
    for date in array_of_formatted_dates:
        resp = requests.get(furl.format(prod_name, date))
        current_price = resp.json()["market_data"]["current_price"]["usd"]

        logger.debug("> "+ date + ":: currentPrice = "+ str(current_price))

        val = round(current_price * prod_amount, 5)
        result_list.append((date, current_price, val))
        
        time.sleep(41) #maybe use a random num 

    return result_list

def generateFormatedDates(start_date, end_date, cycle_len=7, date_fmt="%d-%m-%Y"):
    """
    Calculates the number of cycles based off the start and end dates, and the 
    provided cycle length. Then finds and collects the first date of each cycle.

    :param start_date: Start of time period
    :param end_date:   End of time period
    :param cycle_len:  Length, in days, of a cycle
    :param date_fmt:   String format for datetime objects
    :returns:         The list of relevant dates
    """

    curr_date = start_date
    step_delta = timedelta(days = cycle_len)
    day_diff = (end_date - start_date).days
    num_of_periods = day_diff / cycle_len

    logger.debug("> num_of_periods: "+ str(num_of_periods))

    formatted_dates = []
    formatted_dates.append(start_date)
    for i in range(int(num_of_periods)):
        curr_date += step_delta
        logger.debug(curr_date)

        formatted_date = datetime.strftime(curr_date, date_fmt)
        formatted_dates.append(formatted_date)

    logger.debug("Collected "+ str(len(formatted_dates)) + " dates for " + 
            str(int(num_of_periods)) +" cycles of len " + str(cycle_len))
    return formatted_dates


def prettyDate(datetime_obj):
    return datetime.strftime(datetime_obj, "%a, %d %b %Y")


#no need to handle errors in here
if __name__ == "__main__":

    with open("queryMaker_config.yml", "r") as f:
        configDict = yaml.safe_load(f)

    main(**configDict)


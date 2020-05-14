#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraping Air BnB Laid-Off Workers
@author: RobertTeresi
"""

# Import Libraries
from selenium import webdriver  # Webdriver base class
import pandas as pd  # For easily saving csv
import functools  # For custom error handling metaclass
from datetime import datetime
from datetime import timedelta
import pause  # Easy daily scheduling


# Parameters
repeat_daily = True
custom_datetime = None  # Enter a datetime object to change start time

#  Define File Path
date = datetime.strftime(datetime.now(), "%m_%d_%y")
path = "/Users/RobertTeresi/Dropbox/Airbnb_Scrapes/airbnb_furloughed_" + \
    date+".csv"

# Define Geckodriver path
geckodriver_path = r'/anaconda3/lib/python3.7/geckodriver'

def catch_exception(f):
    """Run function and return error message and traceback if appropriate."""
    @functools.wraps(f)
    def func(*args, **kwargs):
        # It tries to run the function
        try:
            return f(*args, **kwargs)

        # And, if there's an error...
        except StopIteration:
            return f(*args, **kwargs)
        except Exception:

            # It gives us the name of the function that we caught the error in
            print('\n ERROR! \n Caught an exception in the ', f.__name__,
                  " function \n\n")

            # And the full traceback
            raise
    return func


class ErrorCatcher(type):
    """Metaclass returns user-defined error message for class functions."""

    def __new__(cls, name, bases, dct):
        """Wrap all of the functions in the class with the catch_exception."""
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = catch_exception(dct[m])
        return type.__new__(cls, name, bases, dct)


def try_except(try_fun, fail_return=None):
    """Try Except function (for inline try-except clauses).

    Outputs None if exception.
    """
    try:
        # Enter nonsense variable for FUN that doesn't depend on input
        return(try_fun(999))
    except Exception:
        return(fail_return)


class Employee:
    """Employee card class.

    Parses data from employee cards and holds it in a dict.
    """

    def __init__(self, webelement):
        """Initialize class."""
        try:
            # Try to click read more button
            webelement.find_element_by_css_selector('button').click()
        except Exception:
            pass

        self.data = dict({
                        "name": try_except(lambda y: webelement.
                                           find_element_by_css_selector('._1c6z97j').
                                           get_attribute('innerText')),
                        "position": try_except(lambda y: webelement.
                                                find_elements_by_css_selector('._17j792vp')[0].
                                                get_attribute('innerText')),
                        "location": try_except(lambda y: webelement.
                                                find_elements_by_css_selector('._17j792vp')[1].
                                                get_attribute('innerText')),
                        "social_media": try_except(lambda y: [x.
                                                               get_attribute('innerText') + ":" + x.get_attribute('href')
                                                               for x in webelement.find_elements_by_css_selector('._1tcxgp3')
                                                               if x.get_attribute('innerText') != "Resume"]),
                        "resume": try_except(lambda y: [x.get_attribute('href')
                                                        for x in webelement.find_elements_by_css_selector('._1tcxgp3')
                                                        if x.get_attribute('innerText') == "Resume"]),
                        "about": try_except(lambda x: webelement.find_element_by_css_selector('._yz1jt7x').get_attribute('innerText'))
        })


class airbnb_scraper(webdriver.Firefox, metaclass=ErrorCatcher):
    """Driver Class.

    Controls web browser and exports employee data to csv
    """

    def __init__(self, driver_path=geckodriver_path):
        """Initialize Class."""
        # Initialize parent class (starts Firefox web browser)
        super(airbnb_scraper, self).__init__(executable_path=driver_path)

        # Set the implicit wait time to 8 seconds
        self.implicitly_wait(8)

        # Make a list container for employee cards
        self.employees = list()

    def scrape(self):
        """Goes to page and gets all employee cards from it."""
        self.get("http://airbnb.com/d/talent?function=&location=&uuid=&relocation=&remote=&page=1")
        next_page_exists = True
        while next_page_exists:
            try:
                self.find_element_by_css_selector("a [aria-label='Next']")
            except Exception:
                next_page_exists = False

            # Set implicit wait time to a low amount for Employee classes,
            # since we know that the page is already loaded by now.
            self.implicitly_wait(0.1)

            # Create list of Employee card class instances
            self.employees += [Employee(x) for x in
                               self.find_elements_by_css_selector("._1jgihvq")]
            self.implicitly_wait(8)
            if next_page_exists:
                self.find_element_by_css_selector(
                    "a [aria-label='Next']").click()
            else:
                next_page_exists = False
        self.close()

    def to_csv(self, path):
        """Export data from Employee Card Classes into a csv."""
        # Define the pandas dataframe
        csvout = pd.DataFrame(columns=['name',
                                       'position',
                                       'location',
                                       'social_media',
                                       'resume',
                                       'about'])

        # Fill it with the data from the Employee cards
        for employee in self.employees:
            csvout = csvout.append(employee.data, ignore_index=True)
        csvout.to_csv(path)


def main(path):
    """Initialize the scraper, tell it to scrape, and export results."""
    scraper = airbnb_scraper()
    scraper.scrape()
    scraper.to_csv(path)


def schedule(custom_datetime=None):
    """Schedule Script to run every day."""
    if not custom_datetime:
        tomorrow = datetime.now() + timedelta(days=1)
        date
        run_time = datetime(2020, tomorrow.month, tomorrow.day, 8, 0)
        pause.until(run_time)
    else:
        pause.until(custom_datetime)


# Run the main function if this is main script
if __name__ == "__main__":
    while 1:
        if repeat_daily:
            schedule(custom_datetime)  # Default every day at 8am
            main(path)
        else:
            main(path)

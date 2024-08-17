"""
A program designed to search for available classes at Texas A&M University.

This module contains the core functionality of the class search system,
encompassing data retrieval, filtering, and display mechanisms.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

# Setup WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL that contains the AG-Grid
url = 'https://howdy.tamu.edu/uPortal/p/public-class-search-ui.ctf1/max/render.uP?pCp'
driver.get(url)

# Wait for the dynamic content to load
time.sleep(10) # TODO: make this asynchronous

# Here you would use Selenium's functionality to interact with the grid
# For example, find elements by XPath, CSS selectors, etc.
# This depends heavily on how the data is structured in the AG-Grig

# Get the initial scroll height of the grid elem
grid_data = driver.find_elements(By.ID, 'courseSectionsGrid')

# Extract text or any other attribute from the elements

soup = BeautifulSoup(str(grid_data[0].get_attribute('innerHTML')), "html.parser")

for i in soup.findAll('ag-body-viewport ag-selectable ag-layout-normal ag-row-no-animation'):
    print(i)

# Clean up
driver.quit()

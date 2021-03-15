
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
# Path to chromedriver
#!which chromedriver

def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# ### JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Find the relative image url
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None
    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url

# Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    #items = browser.find_by_css('a.product-item h3')
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in range(4):
        #create empty dictionary
        #hemispheres = {}
        browser.find_by_css('a.product-item h3')[i].click()
        #element = browser.links.find_by_text('Sample').first
        #img_url = element['href']
        #title = browser.find_by_css("h2.title").text
        #hemispheres["img_url"] = img_url
        #hemispheres["title"] = title
        hemisphere_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemisphere_data)
        browser.back()
    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # parse html text
    hemisphere_soup = soup(html_text, "html.parser")
    # adding try/except for error handling
    try:
        title_mars = hemisphere_soup.find("h2", class_="title").get_text()
        sample_mars = hemisphere_soup.find("a", text="Sample").get("href")
    except AttributeError:
        # Image error will return None, for better front-end handling
        title_mars = None
        sample_mars = None
    hemispheres = {
        "title": title_mars,
        "img_url": sample_mars
    }
    return hemispheres

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

# browser.quit()

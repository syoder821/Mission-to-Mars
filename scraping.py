# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
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
        "hemisphere_images": mars_hemisphere_data(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# Define function to get latest new from mars nasa news site
def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# Define function to return image
def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


# ## Mars Facts
def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe  
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


def mars_hemisphere_data(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # 2. Create a list to hold the images and titles.
    hemispheres={}
    hemisphere_image_urls = []
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    results = img_soup.find_all("div", class_="description")
    # loop through the results
    for result in results:
        # Find the titles
        title = result.find("a", class_= "itemLink product-item").get_text()
        #print(title)
        # Get the location for the full .jpg image 
        img_loc = result.find('a')["href"]
        # go to the link for the image
        browser.visit(url + img_loc)
        html = browser.html
        # gather html data for the initial image location
        initial_link = soup(html, 'html.parser')
        # Fing the image in dowloads
        thread = initial_link.find('div', class_='downloads')
        img_url = url + thread.a['href']
        #print(img_url)
        # Add image to the and title to dictionary
        hemispheres = {'image_url': img_url, 'title': title}
        # Append dict to list
        hemisphere_image_urls.append(hemispheres)

    # Strip \n from text in the list
    for item in hemisphere_image_urls:
        for key, value in item.items():
            item[key] = value.strip()
        
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())








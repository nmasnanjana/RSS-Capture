import requests
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from flask import Flask, Response

app = Flask(__name__)


def create_rss_feed(articles):
    # Create the root element for the RSS feed
    rss = Element('rss', attrib={'version': '2.0'})
    channel = SubElement(rss, 'channel')

    # Add channel information
    title = SubElement(channel, 'title')
    title.text = 'Latest News Feed'
    link = SubElement(channel, 'link')
    link.text = 'https://www.thepapare.com/latest-news/'
    description = SubElement(channel, 'description')
    description.text = 'Latest news feed from ThePapare'

    # Add articles to the RSS feed
    for article in articles:
        item = SubElement(channel, 'item')
        item_title = SubElement(item, 'title')
        item_title.text = article['title']
        item_description = SubElement(item, 'description')
        item_description.text = article['description']
        item_link = SubElement(item, 'link')
        item_link.text = article['link']
        item_pub_date = SubElement(item, 'pubDate')
        item_pub_date.text = article['published_date']
        if article['image']:
            item_image = SubElement(item, 'enclosure', attrib={'url': article['image'], 'type': 'image/jpeg'})

    # Return the XML string representation of the RSS feed
    return tostring(rss, encoding='unicode')


def scrape_webpage(url):
    # Send a GET request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the news articles on the webpage
        articles = soup.find_all('div', class_='td_module_10 td_module_wrap td-animation-stack')

        # Create a list to store article information
        article_list = []

        # Iterate through each article
        for article in articles:
            # Extract title
            title_tag = article.find('h3', class_='entry-title')
            title = title_tag.find('a')['title'] if title_tag else None

            # Extract Description
            description = article.find('div', class_='td-excerpt').text.strip()

            # Extract link
            link_tag = article.find('div', class_='td-module-thumb')
            link = link_tag.find('a')['href'] if link_tag else None

            # Extract published date
            published_date = article.find('time')['datetime']

            # Extract image URL if available
            image = link_tag.find('img')['data-img-url'] if article.find('img') else None

            # Append article information to the list
            article_info = {
                'title': title,
                'description': description,
                'link': link,
                'published_date': published_date,
                'image': image
            }
            article_list.append(article_info)

        # Return the list of article information
        return article_list

    else:
        print("Failed to fetch the webpage:", response.status_code)
        return []


@app.route('/1928/newrss/latest-lews/')
def rss():
    # URL of the webpage
    webpage_url = "https://www.thepapare.com/latest-news/"

    # Scrape the webpage
    articles = scrape_webpage(webpage_url)

    # Generate RSS feed
    rss_feed = create_rss_feed(articles)

    # Return RSS feed as response
    return Response(rss_feed, mimetype='text/xml')


if __name__ == "__main__":
    app.run()

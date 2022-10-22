from scraper import WebScraper


def main():
    scraper = WebScraper()
    scraper.login()
    scraper.crawl_and_scrape()
    scraper.logout()


if __name__ == "__main__":
    main()

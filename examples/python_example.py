from extract_api import ExtractAPI

api = ExtractAPI()
page = api.extract("https://en.wikipedia.org/wiki/Web_scraping")
print(page["title"], "|", page["word_count"], "words")
print(page["markdown"][:400])

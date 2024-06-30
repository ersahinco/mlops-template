"""
In this file, we collect snippets of code that help you to access all the necessary information from arxiv.org API
that is requested in the coding challenge.
"""

import feedparser
import requests

YOUR_CUSTOM_QUERY="au:Einstein"

# compose URL for arxiv.org API
url = f"https://export.arxiv.org/api/query?search_query={YOUR_CUSTOM_QUERY}&skip=0&max_results=1&sortBy=relevance&sortOrder=descending"

# query arxiv.org with the URL
response = requests.get(url, verify=False)

# add OpenSearch specification to _FeedParserMixin.namespace under key 'opensearch', which defines a standard for
# representing search results in RSS or Atom feeds
feedparser.mixin._FeedParserMixin.namespaces["http://a9.com/-/spec/opensearch/1.1/"] = "opensearch"
# add arxiv namespace to _FeedParserMixin.namespace under key 'arxiv', which defines the arXiv Atom feed
feedparser.mixin._FeedParserMixin.namespaces["http://arxiv.org/schemas/atom"] = "arxiv"

# parse response content
feed = feedparser.parse(response.content)


# access the query
query = feed.get("feed").get("title")

# access the total number of results
total_results = feed.get("feed").get("opensearch_totalresults")

# access the response status code
status = response.status_code

# access the time of the query
query_timestamp_str = response.headers["Date"]

# access any of the results in the feed
entries = feed.entries

# access the third entry in the feed (random choice)
feed_entry_i = feed.entries[0]
feed_entry_all = feed.entries

# access author information (returned as list)
list_of_authors = [author.get("name") for author in feed_entry_i.get("authors")]
authors = ", ".join(list_of_authors)

# access title information
title = feed_entry_i.get("title")

# access journal information
journal = feed_entry_i.get("arxiv_journal_ref")


# print the results
print(f"Query: {query}")
print(f"feed: {feed}")

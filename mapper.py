#!/usr/bin/env python
""" A script that creates a sitemap graph of a website given as a command line argument. """

from bs4 import BeautifulSoup
import urllib2
import matplotlib.pyplot as plt
import networkx as nx
import sys
import re
import os
from collections import deque

visitedURLs = {}
stack = deque()
pages = 0
G = nx.Graph()

""" Gets the website name from the url. """
def extractName(url):
    return re.match(r'http[s]*:\/\/((www\.)?([^\/\.]*)).*$', url).group(1)

""" Returns a list with all of the urls linked on the page of the
corresponding soup object
"""
def findLinks(soup):
    atags = soup.find_all('a', href=True)
    links = []

    for tag in atags:
        match = re.match(re.escape(website), tag['href'])
        if re.search(re.escape(website) + r"\.", expandUrl(tag['href']), re.IGNORECASE):
            links.append(expandUrl(tag['href']))

    return links

""" Adds edges between a list of urls and the current page url. """
def addEdges(page, links):
    for link in links:
        G.add_edge(page, link)

""" Adds new links to the stack to be traversed later. """
def addLinks(link):
    try:
        val = visitedURLs[link]
    except:
        visitedURLs[link] = False
        stack.append(link)

""" Turns a url into suitable input for getting the html.
    Specifically: removing content after a ? or a #, and expanding
    relative file paths.
"""
def expandUrl(url):
    url = re.sub(r'\?.*$', "", url)
    url = re.sub(r'#.*$', "", url)

    match = re.search(r"http[s]*:\/\/[^\/]*\/[^\/]*\/[^\/]*\/(.*)$", url)
    if match:
        url = re.sub(re.escape(match.group(1)), "", url)

    matchObj = re.match(r'http[s]*', url)

    if not matchObj:
        return rooturl+url
    else:
        return url

""" Determines whether the url is relative or not. """
def absUrl(url):
    matchObj = re.match(r'http[s]*', url)
    if not matchObj:
        return False
    else:
        return True

""" Visits a given url and adds all links to the graph."""
def traverse(url):
    global pages, stack
    valid = True
    nds = len(G)
    if nds > 500:
        print "Reached node limit"
        return
    else:
        print str(nds) + " Nodes"

    try:
        html_page = urllib2.urlopen(url)
        soup = BeautifulSoup(html_page, "html5lib")
        pages += 1
    except:
        valid = False

    if valid:
        links = findLinks(soup)
        for link in links:
            if link !=  url:
                addLinks(expandUrl(link))

        G.add_node(url)
        G.add_nodes_from(visitedURLs)
        addEdges(url, visitedURLs)

    try:
        traverse(stack.popleft())
    except Exception as e:
        print(e)
        print "Ended traversing."
        return

""" Output all of the urls in visitedURLs to a text file. """
def writeVisitedLinks(website):
    fp = open(website + ".txt", 'w')
    for key, visited in visitedURLs.items():
        fp.write(key + "\n")
    fp.close()

""" Plots the Graph. """
def plotGraph(website):
    plt.figure(figsize=(30,30))
    plt.subplot(111)

    nx.draw(G, node_color='black', node_size=100, width=1)
    plt.savefig(website + ".png")

if __main__ == "__main__":
    try:
        args = sys.argv
        rooturl = args[1]
        rooturl = re.sub(r"\/$", "", rooturl)
        website = extractName(rooturl)
        print "Website name: ", website
    except:
        print "No arguments, please enter a url as an argument"
        exit()

    print "Traversing..."
    traverse(rooturl)
    print "Pages scraped: ", pages
    print "Nodes: ", len(G)

    print "Writing to file..."
    writeVisitedLinks(website)

    print "Plotting..."
    plotGraph(website)

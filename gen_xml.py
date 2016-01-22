#!/usr/bin/env python
import json
import urllib
import urllib2

#from lxml import etree
import xml.etree.cElementTree as ET

SOLR_URL='http://localhost:8080/solr/citeseerx/select'

def build_xml(root, result):
    e = ET.SubElement(root, 'topic')
    e.attrib['number'] = result['site_qid']
    ET.SubElement(e, 'query').text = result['qstr']

def query_solr(query):
    f = {
        'q': query,
        'rows': 5,
        'start': 0,
        #'qt': 'dismax',
        #&hl=true&hl.fragsize=300
        'wt': 'json',
        'fq': 'incol:true'
    }
    param = urllib.urlencode(f)
    url = SOLR_URL + '?' + param
    print "URL: %s" % url
    data = json.load(urllib2.urlopen(url))

    header = data['responseHeader']
    if not header or header['status'] != 0:
        return []

    results = []
    response = data['response']
    numFound = response['numFound']
    print "Found %d documents" % numFound
    docs = response['docs']
    for doc in docs:
        if 'doi' not in doc:
            continue
        doi = doc['doi']
        print "DOI: %s" % doi
        result = {}
        result['qstr'] = query
        result['site_qid'] = doi
        results.append(result)
    print "Got %d documents " % len(results)
    return results

def main():
    results = query_solr('machine learning')
    print results

    root = ET.Element("root")
    for result in results:
        build_xml(root, result)
    print ET.tostring(root)

if __name__ == '__main__':
    main()

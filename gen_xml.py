#!/usr/bin/env python
import argparse
import json
import urllib
import urllib2

import xml.etree.cElementTree as ET


SOLR_URL='http://localhost:8080/solr/citeseerx/select'


def build_xml(root, result):
    e = ET.SubElement(root, 'topic')
    e.attrib['number'] = result['site_qid']
    ET.SubElement(e, 'query').text = result['qstr']


def query_solr(query, n):
    f = {
        'q': query,
        'rows': n,
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
    #print "Found %d documents" % numFound
    docs = response['docs']
    for doc in docs:
        if 'doi' not in doc:
            continue
        doi = doc['doi']
        #print "DOI: %s" % doi
        result = {}
        result['qstr'] = query
        result['site_qid'] = doi
        results.append(result)
    #print "Got %d documents " % len(results)
    return results


def process_one_query(root, query, n):
    results = query_solr(query, n)

    for result in results:
        build_xml(root, result)


def process(inputfile, outputfile, n):
    root = ET.Element("root")

    with open(inputfile) as ins:
        for line in ins:
            query = line.strip()
            process_one_query(root, query, n)

    tree = ET.ElementTree(root)
    tree.write(outputfile)


def main():
    parser = argparse.ArgumentParser(description='Query Solr and save results as XML for TREC OpenSearch.')
    parser.add_argument('--input', required=True, help='specify input file')
    parser.add_argument('--output', required=True, help='specify output file')
    parser.add_argument('--num', required=True, help='number of results for each query')

    args = parser.parse_args()
    process(args.input, args.output, int(args.num))


if __name__ == '__main__':
    main()

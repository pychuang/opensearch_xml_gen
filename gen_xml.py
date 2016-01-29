#!/usr/bin/env python

import argparse
import codecs
import hashlib
import json
import os
import urllib
import urllib2

import xml.etree.cElementTree as ET


SOLR_URL='http://csxindex03.ist.psu.edu:8080/solr/citeseerx/select'
REPOSITORY='/repository'

def generate_site_query_id(query):
    return hashlib.sha1(query).hexdigest()


def query_solr(query, n):
    f = {
        'q': query,
        'rows': n,
        'start': 0,
        'qt': 'dismax',
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

    response = data['response']
    #numFound = response['numFound']
    #print "Found %d documents" % numFound
    return response['docs']


def build_query_list_xml(root, qid, query):
    e = ET.SubElement(root, 'topic')
    e.attrib['number'] = qid
    ET.SubElement(e, 'query').text = query


def path_for_document(doi):
    splitted_doi = doi.split('.')
    dirpath = os.path.join(REPOSITORY, *splitted_doi)
    filepath = os.path.join(dirpath, doi + '.body')
    if not os.path.exists(filepath):
        filepath = os.path.join(dirpath, doi + '.txt')
        if not os.path.exists(filepath):
            return None
    return filepath


def get_document_content(doi):
    path = path_for_document(doi)
    if not path:
        return None
    with codecs.open(path, 'r', 'utf-8') as f:
        return f.read()


def save_doclist(runfile, docdir, qid, solrdocs):
    for doc in solrdocs:
        if 'doi' not in doc:
            continue
        docid = doc['doi']
        if 'title' not in doc:
            continue
        title = doc['title']
        if 'abstract' in doc:
            abstract = doc['abstract']
        else:
            abstract = ''

        # doclist run file
        line = ' '.join([qid, "dontcare", docid, "dontcare", "dontcare", "dontcare"]) + "\n"
        runfile.write(line)

        # docs
        content = get_document_content(docid)
        if not content:
            content = abstract

        f = codecs.open(os.path.join(docdir, docid), "w", "utf-8")
        f.write(title + "\n")
        f.write(content)


def process(inputfile, n, outputfile):
    qlist_file_name = outputfile + ".xml"
    docdir = "docdir"
    runfile_name = outputfile + ".runfile"
    if not os.path.exists(docdir):
        os.makedirs(docdir)

    runfile = open(runfile_name, "w")
    qlist_root = ET.Element("root")

    with open(inputfile) as ins:
        for line in ins:
            query = line.strip()
            solrdocs = query_solr(query, n)
            qid = generate_site_query_id(query)
            build_query_list_xml(qlist_root, qid, query)
            save_doclist(runfile, docdir, qid, solrdocs)

    ET.ElementTree(qlist_root).write(qlist_file_name)


def main():
    parser = argparse.ArgumentParser(description='Query Solr and save results as XML for TREC OpenSearch.')
    parser.add_argument('--input', required=True, help='specify input file')
    parser.add_argument('--output', required=True, help='specify output file')
    parser.add_argument('--num', required=True, help='number of results for each query')

    args = parser.parse_args()
    process(args.input, int(args.num), args.output)


if __name__ == '__main__':
    main()

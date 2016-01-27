# usage
$ ./gen_xml.py --input queries.txt --num 100

# pretty print XML
cat qlist.xml | xmllint --format - > pretty_qlist.xml

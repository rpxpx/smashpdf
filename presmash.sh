
#!/bin/bash

# presmash.sh
#
# bash script to prepare filesystem for smashpdf.py
# 1. relpace all white space in dirs and filenames with '_'
# 2.  convert all .doc/docx .doc.pdf/.docx.pdf
#
# Uses libreoffice for conversion
#
# libreoffice --headless --convert-to pdf a.doc


# REGEX, splits path, filename, extension
# ^/(.+/)*(.+)\.(.+)$
# DIR:
# ^(.+/)*


#deal with spaces in folder and file names: change line separator
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")


# Also convert all directories and file names to remove spaces


if [ $1 ]
then dir=$1
else dir="./"
fi


#calc numvber of doc/docx


# CONVERT ALL DIR FIRST
#
f=$(find $dir -type d -name '*[, ]*'| sort | head -n 1)
while [ $f ]
do
    echo "renaming: "$f
    echo "to: "$(echo $f | sed -e 's/ /_/g'|sed -e 's/,//g')
    echo
    mv $f $(echo $f | sed -e 's/ /_/g'|sed -e 's/,//g')
    f=$(find $dir -type d -name '*[, ]*'| sort | head -n 1)
done


# NOW CONVERT FILES
# strip ',' and replave ' ' with '_'
#
for f in $(find $dir -name '*[, ]*')
do
    #echo $f $(echo $f |rev|sed -e 's/ /_/'|rev)
    echo "renaming: "$f
    echo "to: "$(echo $f|sed -e 's/ /_/g'|sed -e 's/,//g')
    echo
    mv $f $(echo $f|sed -e 's/ /_/g'|sed -e 's/,//g')
    #echo $f $(echo $f|sed -e 's/ /_/g')
done



#COVNERT ALL DOC/DOCX TO PDF

i=$((0))
for f in $(find $dir -name '*.d*[cx]')
do
    #extract folder name from complete file name:
    d=$(echo $f | grep -oE '^(.+/)*')
    
    #stip out file name in same way
    fne=$(echo $f | grep -oE '[^/]+\.(.{3,4})$')
    ext=$(echo $fne | grep -oE '.[^\.]+$')
    fn=$(echo $fne | sed -E -e 's/.docx?//') #strip away extension
    
    echo "CONVERTING "
    echo "file: "$fne
    echo "dir : "$d
    echo
    # echo "dir:  "$d
    # echo "fne:  "$fne
    # echo "ext:  "$ext
    # echo "fn:   "$fn

    libreoffice --headless --convert-to pdf --outdir $d $f
    i=$(($i+1))
    mv $d$fn".pdf" $d$fn$ext".pdf"
    #libreoffice --headless --convert-to pdf $f
    #mv "./"$fn".pdf" $d$fne".pdf"
done

echo "CONVERTED: "$i
echo

find $dir -name '*.d*[cx]'
find $dir -name '*.d*[cx]' | wc -l

find $dir -name '*.d*[cx].pdf'
find $dir -name '*.d*[cx].pdf'|wc -l


#!/usr/bin/python3

# SMASHPDF V0.2
# richard christian, github: rpxpx

# Prerequisites:
# $sudo apt install python3 python3-pip tesseract 
# $pip3 install setuptools wheel pdfminer pytesseract

# Use:
# $smashpdf <keys.txt> $(find <dir> -name '*.pdf')


# LIGHTWEIGHT CSV VIEWER:
# https://www.tadviewer.com/


import io 
import re #regexp library --> ResSearch = re.search(String, Text)
import sys
import pdfminer
import pdfocr #my python lib pdfocr.py
import subprocess
import datetime
import traceback
import logging


from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter

from pdfminer.pdfdevice import PDFDevice

from pdfminer.layout import LAParams

from pdfminer.converter import PDFPageAggregator
from pdfminer.converter import TextConverter




def pdfregex(loc, keys):
    # Receive a pdf location and a dict of regex keys with natural indeces
    # Return a dict of dicts of page numbers w corresponding hits
    # Returns hitsheet and keyhits

    SNIPPET_LENGTH = 225

    fp = open(loc, 'rb')
    # Create a PDF parser object associated with the file object.

    print("1")
    try:
        # Open a PDF file.
        parser = PDFParser(fp)
        print("2")
    except Exception as e:
        print("3")
        logging.error(traceback.format_exc())
        return "FILE:"+loc+"\ncould not be opened. Possibly not a PDF.", {}

    try:
        # Create a PDF document object that stores the document structure.
        document = PDFDocument(parser)    
    except Exception as e:
        #PDF cannot be opened
        print("4")
        logging.error(traceback.format_exc())
        hitsheet="\n{:>10}".format("FILE:")+loc+'\n'+"READ MODE: Could not be opened. Possibly not a PDF\n"
        keyhits = {}
        for k in keys:
            keyhits[k]={0:0}
        print( keyhits )
        print( hitsheet )
        return keyhits, hitsheet

    
    # Check if the document allows text extraction.
    print("\nSCANNING:",loc)
    print("METADATA:",document.info)
    
    # If unreadable, attempt OCR
    if not document.is_extractable:
        # doesn't seem to work properly - leave in for now;
        raise PDFTextExtractionNotAllowed
   
    # If readable, extract text with pdfminer
    else:
        print("PDF looks readable. Attempting to mine text.")
        mode = "MINE"
        
        # Create PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()
        
        # Set parameters & codec for textconversion
        codec = "utf-8"
        laparams = LAParams()
        
        # Process each page contained in the document.
        text = [] #list of strings; each list item is one page
        
        
        for page in PDFPage.create_pages(document): #yields pages though a generator    
            print("Mining p.",len(text)+1)
            retstr = io.StringIO()
            device3 = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            #device3 = TextConverter(rsrcmgr, retstr, laparams=laparams)
            interpreter3 = PDFPageInterpreter(rsrcmgr, device3)
            
            interpreter3.process_page(page) #conversion to plain text
            
            t = retstr.getvalue()
            if len(t)>1:
                text.append( t )
                
            # shutdown page objects
            retstr.close()
            device3.close()
    
        # shut down file
        fp.close()
        
    # If unreadable, attempt OCR
    if text==[]:
        mode = "OCR"
        print("PDF unreadable. Attempting OCR.")
        print(loc)

        text = pdfocr.pdf_to_str(loc)
    
    # Now scan txt for keys
    keyhits = {} #dict of key word hits for each page where >0
    
    # Establish dict of dicts w key indeces; 
    for k in keys:
        keyhits[k]={0:0} 

    # Snippets with hits stored in hitsheet
    
    hitsheet="\n{:>10}".format("FILE:")+loc+'\n'+"READ MODE: "+mode+"\n"
    
    #Nested loop: cycle through keys, cycle through pages in text
    for k in keys:
        #print("KEY:",keys[k])
        hitsheet+='\n'+keys[k]+'\n'+'='*len(keys[k])+'\n'
        
        for p,t in enumerate(text):
            
            # Find all instances of current key in current page
            h=0
            for m in re.finditer(keys[k],t):
                h+=1
                # Extract sample for context
                # List page nubmer and % location in page
                snippet='{:>4}'.format(p+1)+"."+str(int(m.start()/len(t)*100)).zfill(2)+": "+snip(t,m.start(),SNIPPET_LENGTH)
                # Add to hitsheet
                hitsheet += snippet.replace('\n','')+'\n'
                
            
            # l += len(re.findall(keys[k].lower(), t))
            # l += len(re.findall(keys[k].lower().capitalize(), t))
            # l += len(re.findall(keys[k].upper(), t))
            if h > 0:
                #assign hits to page key
                keyhits[k][p+1] = h
                #increase total tally of key hits for doc, stored as p0
                keyhits[k][0]+=h 
                
    return keyhits, hitsheet


def snip(t, p, l):
    """cut out a snippet of length l from str t, preferable centred on p"""
    lt = len(t)
    ugap = lt-p
    lgap = max(l//2, l-ugap)
    s = max(0, p-lgap)
    e = min(lt,s+l)    
    return t[s:e]




def main():
    print("smashpdf, v0.2")
    #open a pdf, read one p at a time, count occurances of a keyword;

    #mkdir
    dt=datetime.datetime.now()
    dn = "./smash-out-"+dt.date().strftime("%Y%m%d")+dt.time().strftime("%H%M")+"/"
    c = "mkdir "+dn
    subprocess.Popen(c, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    
    
    #ERROR CHECK ARGUMENT SEQUENCE
    if len(sys.argv) < 2: #error
        print("smashpdf keys.txt 1.pdf 2.pdf ...")
        return

    
    #KEYS
    keysf = open(str(sys.argv[1]))
    keys = {}
    #keysl = [] #build a separate keys list for CSV header
    k = 0
    for l in keysf.readlines():
        s = str(l).strip()
        if s != "" and s[0]!='#': #ignore empty lines and comments
            k+=1
            keys[k] = str(s)
            #keysl.append(s)
        
    print("KEYS: ",keys)

    #return
    
    
    #CSV OUTPUT PREP
    csvf = open(dn+"smash-out.csv",'w')
    #write header first from keys
    header="ID,DIR,FILE"
    for e in keys:
        header+=","+keys[e]+"  ==TOTAL==,"+keys[e]+"  ==REFS=="
    print(header,file=csvf)

    #CSV SHORT VERSION
    csvfto = open(dn+"smash-out-totalsonly.csv",'w')
    #write header first from keys
    header="ID,DIR,FILE"
    for e in keys:
        header+=","+keys[e]+"  ==TOTAL=="
    print(header,file=csvfto)

    
    
    #MAIN CYCLE THROUGH PDFS
    for i in range(2, len(sys.argv)):
        fname = str(sys.argv[i])
        if fname[-4:] != ".pdf":
            print("Error: arg",fname)
            break
        
        
        #main work
        keyhits, hitsheet = pdfregex(fname, keys) #smash this pdf w keys
        
        # print(keyhits)
        # print(hitsheet)

        
        #Construct CSV entry for file        
        #split passed floc into dir, fn, ext
        d, fn, ext = pdfocr.dfe(fname)
        line = str(i-1).zfill(4)+","+d+","+fn+ext
        line_to = str(i-1).zfill(4)+","+d+","+fn+ext
        
        for j in range(1,len(keys)+1): #cycle through all keys
            line+=","
            line_to+=","
            if j in keyhits:
                line_tot = str(keyhits[j].pop(0)) #add total 
                line_ref = ",\""+str(keyhits[j])[1:-1]+"\""                
                line += line_tot + line_ref
                line_to += line_tot
            else:
                line+="0,"
                line_to+="0,"
        print(line, file=csvf)
        print(line_to, file=csvfto)
    
        #WRITE HITSHEET
        hitsheet_fname = str(i-1).zfill(4)+"-"+fn+ext+".txt"
        hitsheet_f = open(dn + hitsheet_fname, 'w')
        print(hitsheet, file=hitsheet_f)
        print("WRITING: ", hitsheet_fname)
        hitsheet_f.close()
        
    #WRITE CSV
    print("WRITING: out.csv")
    csvf.close()
    csvfto.close()    
    return


main()

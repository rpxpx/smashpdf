# smashpdf
Scan large sets of PDFs for regular expressions, return output in a database and as a set of text files containing text snippets.

The program checks through a set of PDFs passed at command-line, searching page by page through each for the regular expressions contained in a keywords text file, also passed at command-line. The program first attempts to strip out embedded plain text from each page of the PDF. If it can't do that, it assumes that the PDF is a scanned document and attempts to derive text from the page by OCR. If it finds a regex, it records a page number and page position, and a "snippet" of text: a 225 (or whatever) character string with the regex as close to the center as possible. The output consists of a CSV database showing page numbers and positions for each regex/PDF pair, and a set of text files, one for each PDF, containing all the snippets for each regex.

The regex set example included here has to do with agroecology. Comments can be included in the keywords file by prepending '#'.

# py_pubmed
Python script to obtain PubMed data using their public API.

Although a great package exists to obtain in an efficient way PubMed data from their public API, [PyMed](https://github.com/gijswobben/pymed "PyMed at github"), I was interested in gathering information on author affiliations, a type of information that was missing from such package.

In particular, the user should input in l.16 some pubmed ID (PMID), e.g. '20064380' which is a nice paper on RNA polymerases, and by the end of the script a pandas DataFrame will contain information on articles citing that work. The information that I was interested in is: 

- Author
- Affiliation
- Country of the affiliation (simplified name; using [pycountry](https://github.com/flyingcircusio/pycountry "pycountry at github") )
- PMID
- Title
- Journal
- Year of publication

If perhaps you need additional information, do not hesitate to contact me and I'll gladly help.
Hopefully, this script will also help other people learn how to interact with PubMed's API because their documention might seem confusing at first. 


## Example Applications
Using regular pandas and python programming one can easily find, for example:

### i) The number of people that has cited the article: 

	unique_authors = np.unique(df['Author'])

### ii) The number of citations from each author...

	num_citations = np.array([ len( df[ df['Author']==author]) for author in unique_authors ])
or producing images like this one:

![Number of citations from each author](/figure.png)


### iii) Authors with their affiliation in a given country

	_=[ print(x) for x in np.unique( df[ df['Country']=='Spain']['Author'] ) ];`
	
	Bajic, Djordje
	Blanco, P
	Corona, F
	Dolcemascolo, Roswitha
	Elola, Ignacio
	Goiriz, Lucas
	Loureiro, Cristina
	Martínez, J L
	Montagud-Martínez, Roser
	Poyatos, Juan F
	Rodrigo, Guillermo
	Yubero, Pablo

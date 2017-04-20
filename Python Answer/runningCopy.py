#!/usr/bin/python
import sys
import re
import ply.lex as lex
import ply.yacc as yacc

KBSentences = {}
KBIndexes = {}
visitedSentences = {}

tokens = (
				"NOT",
				"CONJUNCTION",
				"DISJUNCTION",
				"IMPLIES",
				"PREDICATE",
				"CONSTANT",
				"VARIABLE",
				"LPAREN",
				"RPAREN",
				"COMMA"
		 )

t_NOT = r'\~'
t_CONJUNCTION = r'\&'
t_DISJUNCTION = r'\|'
t_IMPLIES = r'\=\>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_ignore  = ' \t'

def t_PREDICATE(t):
	r'[A-Z]{1}[a-zA-Z0-9]*\('
	t.value = t.value.rstrip('(')
	return t

def t_CONSTANT(t):
	r'[A-Z]{1}[a-zA-Z0-9]*\)|[A-Z]{1}[a-zA-Z0-9]*'	#might have a right parenthesis at the end
	t.value = t.value.rstrip(')')
	return t

def t_VARIABLE(t):
	r'[a-z]{1}\)|[a-z]{1}'							#might have a right parenthesis at the end
	t.value = t.value.rstrip(')')
	return t

def t_error(t):
	raise TypeError("Unknown text '%s'" % (t.value[0]))
	t.lexer.skip(1)

def p_sentence_predicate(p):
	'''sentence : PREDICATE argument'''
	#print "predicate"
	p[0] = p[1] + '(' + p[2] + ')'

def p_sentence_negation(p):
	'''sentence : LPAREN NOT sentence RPAREN'''
	#print "negation"
	p[0] = p[1] + p[2] + p[3] + p[4]

def p_sentence_implies(p):
	'''sentence : LPAREN sentence IMPLIES sentence RPAREN'''
	#print "implies"
	p[0] = '((~' + p[2] + ')|' + p[4] + ')'

def p_sentence_demorgan(p):
	'''sentence : LPAREN NOT LPAREN sentence CONJUNCTION sentence RPAREN RPAREN
				| LPAREN NOT LPAREN sentence DISJUNCTION sentence RPAREN RPAREN'''
	if p[5] == '&':
		#print "Demorgan on AND"
		p[0] = p[1] + p[1] + p[2] + p[4] + p[7] + '|' + p[3] + p[2] + p[6] + p[7] + p[8]
	elif p[5] == '|':
		#print "Demorgan on OR"
		p[0] = p[1] + p[1] + p[2] + p[4] + p[7] + '&' + p[3] + p[2] + p[6] + p[7] + p[8]

def p_sentence_double_negation(p):
	'''sentence : LPAREN NOT LPAREN NOT sentence RPAREN RPAREN'''
	#print "double negation"
	p[0] = p[5]

def p_sentence_distribute(p):
	'''sentence : LPAREN LPAREN sentence CONJUNCTION sentence RPAREN DISJUNCTION sentence RPAREN
				| LPAREN sentence DISJUNCTION LPAREN sentence CONJUNCTION sentence RPAREN RPAREN'''	#distribute OR over AND
	if p[4] == '&':
		#print "distribute OR behind"
		p[0] = p[1] + p[2] + p[3] + p[7] + p[8] + p[6] + p[4] + p[1] + p[5] + p[7] + p[8] + p[9] + p[9]
	elif p[3] == '|':
		#print "distribute OR front"
		p[0] = p[1] + p[4] + p[2] + p[3] + p[5] + p[8] + p[6] + p[1] + p[2] + p[3] + p[7] + p[8] + p[9]

def p_sentence_binary(p):
	'''sentence : LPAREN sentence RPAREN
				| LPAREN sentence CONJUNCTION sentence RPAREN
				| LPAREN sentence DISJUNCTION sentence RPAREN'''
	if len(p) == 4:
		#print "sentence length 4"
		p[0] = p[2]
	elif len(p) == 6:
		#print "sentence length 6"
		p[0] = p[1] + p[2] + p[3] + p[4] + p[5]

def p_argument(p):
	'''argument	: argument COMMA argument
				| CONSTANT
				| VARIABLE'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = p[1] + p[2] + p[3]

def p_error(p):
	print("Syntax error in input!")

def convertSentenceToCNF(s, lexer, parser):
	lexer.input(s)
	cnf = parser.parse(s)
	while not cnf == s:
		s = cnf
		cnf = parser.parse(s)
	#print "CNF : "+cnf

	#remove all the unnecessary parentheses
	cnf = re.sub(r'\(([a-z]{1}[a-z,A-Z0-9]*|[A-Z]{1}[a-zA-Z0-9,]*)\)',r'{\1}',cnf)	  #replacing the parentheses around arguments with braces
	cnf = re.sub(r'\(|\)','',cnf)
	cnf = re.sub('{','(',cnf)
	cnf = re.sub('}',')',cnf)
	return cnf

def addEntryToKBI(lit, counter):
	global KBIndexes
	predicateName = lit.split('(')[0]
	if not predicateName in KBIndexes:
		KBIndexes[predicateName] = []
	if not counter in KBIndexes[predicateName]:
		KBIndexes[predicateName].append(counter)		#store the line number in KBSentences where the current predicate appears

def populateKB(sentences):
	global KBIndexes, KBSentences
	lexer = lex.lex()
	parser = yacc.yacc()
	counter = 0
	#convert sentences from input file
	for s in sentences:
		s = re.sub(' ','',s)
		s = re.sub('\t','',s)
		#print "Current sentence : "+s
		cnf = convertSentenceToCNF(s, lexer, parser)
		#print "New CNF : "+cnf

		disjunctions = cnf.split('&')
		for disjunc in disjunctions:				#disjunc... = Abc(x,y)|~Bac(Bill,x)|Dba(z,y)
			counter = counter + 1
			KBSentences[counter] = disjunc
			literals = disjunc.split('|')
			for lit in literals:					#lit = Abc(x,y), ~Bac(Bill,x), Dba(z,y)
				addEntryToKBI(lit, counter)
	print "KB Sentences : "+str(KBSentences)
	print "KB Indexes : "+str(KBIndexes)
	return

def getNegationOfLiteral(q):
	if '~' in q:
		return q.lstrip('~')
	else:
		return '~'+q

def unify(argumentsFromCS, argumentsFromKB):
	csArgArr = argumentsFromCS.split(',')
	kbArgArr = argumentsFromKB.split(',')
	csUnificationValues = {}
	kbUnificationValues = {}
	for i in range(len(kbArgArr)):
		if re.match(r'[A-Z]{1}[A-Za-z0-9]*',kbArgArr[i]) and re.match(r'[A-Z]{1}[A-Za-z0-9]*',csArgArr[i]) and not kbArgArr[i] == csArgArr[i]:	#if both arg are constants
			return None		#can't unify
		elif re.match(r'[A-Z]{1}[A-Za-z0-9]*',kbArgArr[i]) and re.match(r'[a-z]{1}',csArgArr[i]):
			if not csArgArr[i] in csUnificationValues:
				csUnificationValues[csArgArr[i]] = kbArgArr[i]
			elif not csUnificationValues[csArgArr[i]] == kbArgArr[i]:	#value exist but is different from what we are trying to assign
				return None
		elif re.match(r'[A-Z]{1}[A-Za-z0-9]*',csArgArr[i]) and re.match(r'[a-z]{1}',kbArgArr[i]):
			if not kbArgArr[i] in kbUnificationValues:
				kbUnificationValues[kbArgArr[i]] = csArgArr[i]
			elif re.match(r'[a-z]{1}',kbUnificationValues[kbArgArr[i]]):
				csUnificationValues[kbUnificationValues[kbArgArr[i]]] = csArgArr[i]
				kbUnificationValues[kbArgArr[i]] = csArgArr[i]
			elif not kbUnificationValues[kbArgArr[i]] == csArgArr[i]:	#value exist but is different from what we are trying to assign
				return None
		else:		#both are variables
			if kbArgArr[i] in kbUnificationValues and csArgArr[i] in csUnificationValues:
				if re.match(r'[A-Z]{1}[A-Za-z0-9]*',kbUnificationValues[kbArgArr[i]]) and re.match(r'[A-Z]{1}[A-Za-z0-9]*',csUnificationValues[csArgArr[i]]) and not kbUnificationValues[kbArgArr[i]] == csUnificationValues[csArgArr[i]]:
					return None
			elif kbArgArr[i] in kbUnificationValues:
				csUnificationValues[csArgArr[i]] = kbUnificationValues[kbArgArr[i]]
			elif csArgArr[i] in csUnificationValues:
				kbUnificationValues[kbArgArr[i]] = csUnificationValues[csArgArr[i]]
			else:
				kbUnificationValues[kbArgArr[i]] = csArgArr[i]
	unificationValues = {'forKB':kbUnificationValues, 'forCS':csUnificationValues}
	return unificationValues

#unify the max 100 arguments and resolve the sentences
#literalToUnify will be in currentSentences
def unifyAndResolve(sentenceFromKB, currentSentences, literalFromCS, literalFromKB):
	print "Here to unify : "+sentenceFromKB+" and "+currentSentences
	print "Literal from CS : "+literalFromCS+" :: literal from KB : "+literalFromKB
	argumentsFromCS = literalFromCS.split('(')[1].rstrip(')')
	argumentsFromKB = literalFromKB.split('(')[1].rstrip(')')
	unificationValues = unify(argumentsFromCS, argumentsFromKB)
	print "KB Arguments : "+argumentsFromKB+" :: CS Arguments : "+argumentsFromCS+" :: Unification Values : "+str(unificationValues)
	if unificationValues is None:
		return None
	#variable can occur in the forms - (x), (x,....), (...,x,....), (....,x)
	for item in unificationValues['forKB']:
		sentenceFromKB = re.sub(r'\('+item+'\)', '('+unificationValues['forKB'][item]+')', sentenceFromKB)	#(x)
		sentenceFromKB = re.sub(r'\('+item+',', '('+unificationValues['forKB'][item]+',', sentenceFromKB)		#(x,...)
		sentenceFromKB = re.sub(r','+item+',', ','+unificationValues['forKB'][item]+',', sentenceFromKB)		#(....,x,...)
		sentenceFromKB = re.sub(r','+item+'\)', ','+unificationValues['forKB'][item]+')', sentenceFromKB)	#(....,x)
		literalFromKB = re.sub(r'\('+item+'\)', '('+unificationValues['forKB'][item]+')', literalFromKB)	#(x)
		literalFromKB = re.sub(r'\('+item+',', '('+unificationValues['forKB'][item]+',', literalFromKB)		#(x,...)
		literalFromKB = re.sub(r','+item+',', ','+unificationValues['forKB'][item]+',', literalFromKB)		#(....,x,...)
		literalFromKB = re.sub(r','+item+'\)', ','+unificationValues['forKB'][item]+')', literalFromKB)	#(....,x)
	for item in unificationValues['forCS']:
		currentSentences = re.sub(r'\('+item+'\)', '('+unificationValues['forCS'][item]+')', currentSentences)
		currentSentences = re.sub(r'\('+item+',', '('+unificationValues['forCS'][item]+',', currentSentences)
		currentSentences = re.sub(r','+item+',', ','+unificationValues['forCS'][item]+',', currentSentences)
		currentSentences = re.sub(r','+item+'\)', ','+unificationValues['forCS'][item]+')', currentSentences)
		literalFromCS = re.sub(r'\('+item+'\)', '('+unificationValues['forCS'][item]+')', literalFromCS)
		literalFromCS = re.sub(r'\('+item+',', '('+unificationValues['forCS'][item]+',', literalFromCS)
		literalFromCS = re.sub(r','+item+',', ','+unificationValues['forCS'][item]+',', literalFromCS)
		literalFromCS = re.sub(r','+item+'\)', ','+unificationValues['forCS'][item]+')', literalFromCS)
	newCS = ''
	print "Updated KB sentence : "+sentenceFromKB+" :: Updated CS sentence : "+currentSentences
	KBArr = sentenceFromKB.split('|')
	for literalKB in KBArr:
		if not literalFromKB == literalKB:
			newCS += literalKB+'|'
	CSArr = currentSentences.split('|')
	for literalCS in CSArr:
		if not literalCS == literalFromCS:
			newCS += literalCS+'|'
	newCS = newCS.rstrip('|')
	if newCS == '':
		newCS = 'contradiction'
	return newCS

def findResolution(currentSentences):
	print "\nCurrent Sentence : "+currentSentences
	global KBIndexes, KBSentences, visitedSentences
	if currentSentences == 'contradiction':
		return True
	else:
		visitedSentences[currentSentences] = 1
	csLiterals = currentSentences.split('|')
	print "CS Literals : "+str(csLiterals)
	for literal in csLiterals:
		negatedLiteral = getNegationOfLiteral(literal)
		predicateNegatedLiteral = negatedLiteral.split('(')[0]
		linesToUnifyWithCS = KBIndexes[predicateNegatedLiteral]
		print literal+" can be resolved with lines : "+str(linesToUnifyWithCS)
		for line in linesToUnifyWithCS:
			#line can have multiple predicates that can unify the current literal
			kbLiterals = KBSentences[line].split('|')
			for kbLiteral in kbLiterals:
				if kbLiteral.split('(')[0] == predicateNegatedLiteral:
					newCS = unifyAndResolve(KBSentences[line], currentSentences, literal, kbLiteral)
					print "Unified "+currentSentences+" with "+str(KBSentences[line])+" to get : "+str(newCS)
					if newCS is None:		#this condition is true when the sentences fail to unify and resolve
						continue
					#print visitedSentences
					if not newCS in visitedSentences and findResolution(newCS):
						return True
	return False

def checkQueries(queries):
	global KBSentences, KBIndexes, visitedSentences
	outputs = []
	for q in queries:
		q = re.sub(' ','',q)
		q = re.sub('\t','',q)
		visitedSentences = {}
		index = len(KBSentences) + 1
		#negate the query and add to KB
		KBSentences[index] = getNegationOfLiteral(q)
		addEntryToKBI(KBSentences[index], index)
		queryResult = findResolution(KBSentences[index])
		outputs.append(queryResult)
		#remove the negated element from KBSentences and KBIndexes
		predicateName = KBSentences[index].split('(')[0]
		del KBSentences[index]
		if len(KBIndexes[predicateName]) == 1:
			del KBIndexes[predicateName]
		else:
			KBIndexes[predicateName].remove(index)
		#if the query is true then add it to KB
		if queryResult:
			KBSentences[index] = q
			addEntryToKBI(KBSentences[index], index)
		print KBSentences
		print KBIndexes
	return outputs

def readInputFile(fileName):
	file = open(fileName, 'r')
	returnVal = {}
	returnVal['nQueries'] = int(file.readline().rstrip('\n').rstrip('\r'))

	i = 0
	queries = []
	while i < returnVal['nQueries']:
		queries.append(file.readline().rstrip('\n').rstrip('\r'))
		i += 1

	returnVal['queries'] = queries

	returnVal['nSentences'] = int(file.readline().rstrip('\n').rstrip('\r'))
	i = 0
	sentences = []
	while i < returnVal['nSentences']:
		sentences.append(file.readline().rstrip('\n').rstrip('\r'))
		i += 1

	returnVal['sentences'] = sentences

	file.close()
	return returnVal

def testCNFConversion():
	file = open('checkTheseSentences', 'r')
	cnfOutput = open('cnfOutput.txt','w')
	lexer = lex.lex()
	parser = yacc.yacc()
	while 1:
		s = file.readline().rstrip('\n').rstrip('\r')
		if not s:
			break
		s = re.sub(' ','',s)
		s = re.sub('\t','',s)
		print "Parsing : "+s
		lexer.input(s)
		cnf = parser.parse(s)
		while not cnf == s:
			s = cnf
			cnf = parser.parse(s)
		cnfOutput.write("%s\n" % cnf)
	cnfOutput.close()
	file.close()

def createOutputFile(output):
	outputFile = open("output.txt", 'w')
	for value in output:
		if value:
			outputLine = "TRUE\n"
		else:
			outputLine = "FALSE\n"
		outputFile.write(outputLine)
	outputFile.close()

def main():
	fileData = readInputFile("input.txt")
	print (fileData)
	#testCNFConversion()
	populateKB(fileData['sentences'])
	output = checkQueries(fileData['queries'])
	print output
	createOutputFile(output)

main()

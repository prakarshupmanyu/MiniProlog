#!/usr/bin/python
import sys
import re
import ply.lex as lex
import ply.yacc as yacc
import string

KBSentences = {}
KBIndexes = {}
visitedSentences = {}
csLiteralBeingUnified = {}
literalsThatCannotBeUnified = {}

tokens = (
				"NOT",
				"CONJUNCTION",
				"DISJUNCTION",
				"IMPLIES",
				"PREDICATE",
				"LPAREN",
				"RPAREN",
		 )

t_NOT = r'\~'
t_CONJUNCTION = r'\&'
t_DISJUNCTION = r'\|'
t_IMPLIES = r'\=\>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore  = ' \t'

def t_PREDICATE(t):
	r'[A-Z]{1}[a-zA-Z0-9]*_l_[a-zA-Z0-9,]*_r_'
	return t

def t_error(t):
	raise TypeError("Unknown text '%s'" % (t.value[0]))
	t.lexer.skip(1)

def p_sentence_predicate(p):
	'''sentence : PREDICATE'''
	p[0] = p[1]
	#print "predicate : "+p[0]

def p_sentence_negation(p):
	'''sentence : LPAREN NOT PREDICATE RPAREN'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	#print "negation : "+p[0]

def p_sentence_implies(p):
	'''sentence : LPAREN sentence IMPLIES sentence RPAREN'''
	p[0] = '((~' + p[2] + ')|' + p[4] + ')'
	#print "implies : "+p[0]

def p_sentence_in_negation(p):
	'''sentence : LPAREN NOT LPAREN sentence RPAREN RPAREN'''
	p[0] = p[1] + p[2] + p[4] + p[5]
	#print "Take negation in : "+p[0]

def p_sentence_demorgan(p):
	'''sentence : LPAREN NOT LPAREN sentence CONJUNCTION sentence RPAREN RPAREN
				| LPAREN NOT LPAREN sentence DISJUNCTION sentence RPAREN RPAREN'''
	if p[5] == '&':
		p[0] = p[1] + p[1] + p[2] + p[4] + p[7] + '|' + p[3] + p[2] + p[6] + p[7] + p[8]
		#print "Demorgan on AND : "+p[0]
	elif p[5] == '|':
		p[0] = p[1] + p[1] + p[2] + p[4] + p[7] + '&' + p[3] + p[2] + p[6] + p[7] + p[8]
		#print "Demorgan on OR : "+p[0]

def p_sentence_double_negation(p):
	'''sentence : LPAREN NOT LPAREN NOT sentence RPAREN RPAREN'''
	p[0] = p[5]
	#print "double negation : "+p[0]

def p_sentence_distribute(p):
	'''sentence : LPAREN LPAREN sentence CONJUNCTION sentence RPAREN DISJUNCTION sentence RPAREN
				| LPAREN sentence DISJUNCTION LPAREN sentence CONJUNCTION sentence RPAREN RPAREN'''	#distribute OR over AND
	if p[4] == '&':
		p[0] = p[1] + p[2] + p[3] + p[7] + p[8] + p[6] + p[4] + p[1] + p[5] + p[7] + p[8] + p[9] + p[9]
		#print "distribute OR behind : "+p[0]
	elif p[3] == '|':
		p[0] = p[1] + p[4] + p[2] + p[3] + p[5] + p[8] + p[6] + p[1] + p[2] + p[3] + p[7] + p[8] + p[9]
		#print "distribute OR front : "+p[0]

def p_sentence_binary(p):
	'''sentence : LPAREN sentence RPAREN
				| LPAREN sentence CONJUNCTION sentence RPAREN
				| LPAREN sentence DISJUNCTION sentence RPAREN'''
	if len(p) == 4:
		p[0] = p[2]
		#print "sentence length 4 : "+p[0]
	elif len(p) == 6:
		p[0] = p[1] + p[2] + p[3] + p[4] + p[5]
		#print "sentence length 6 : "+p[0]

def p_error(p):
	print("Syntax error in input!")

def convertSentenceToCNF(s, lexer, parser):
	cnf = parser.parse(s)
	while not cnf == s:
		s = cnf
		cnf = parser.parse(s)
		#print "CNF : "+cnf

	#remove all the unnecessary parentheses
	cnf = re.sub(r'\(|\)','',cnf)
	cnf = re.sub('_l_','(',cnf)
	cnf = re.sub('_r_',')',cnf)
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
		s = re.sub(r'([A-Z]{1}[a-z0-9A-Z]*)\({1}([a-zA-Z0-9,]*)\){1}',r'\1_l_\2_r_',s)
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
	#print "KB Sentences : "+str(KBSentences)
	#print "KB Indexes : "+str(KBIndexes)
	return

def getNegationOfLiteral(q):
	if '~' in q:
		return q.lstrip('~')
	else:
		return '~'+q

#add the current sentence to the list of visitied sentences. Take care of the permutations
def addCSToVisitiedSentences(CS):
	global visitedSentences
	CSArray = CS.split("|")
	CSArray.sort()
	CS = "|".join(CSArray)
	visitedSentences[CS] = 1

#check whether a given sentence or its permutaion is already present in visited sentences or not
def isNewCSInVisitedSentences(CS):
	global visitedSentences
	#print "Currently visited sentences : "+str(visitedSentences)
	CSArray = CS.split("|")
	CSArray.sort()
	CS = "|".join(CSArray)
	if CS in visitedSentences:
		return True
	return False

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

def getVariableArgumentList(literalsList):
	argList = []
	for literal in literalsList:
		literalArg = literal.split('(')[1].rstrip(')')
		argList.extend(filter(lambda x: len(x) == 1 and re.match(r'[a-z]',x), literalArg.split(',')))
	return list(set(argList))

def getNewVariable(list1, list2):
	for v in list(string.ascii_lowercase):
		if not v in list1 and not v in list2:
			return v

#variable can occur in the forms - (x), (x,....), (...,x,....), (....,x)
def replaceArgumentInSentence(argToReplace, newValue, sentence):
	sentence = re.sub(r'\('+argToReplace+'\)', '('+newValue+')', sentence)	#(x)
	sentence = re.sub(r'\('+argToReplace+',', '('+newValue+',', sentence)		#(x,...)
	sentence = re.sub(r','+argToReplace+',', ','+newValue+',', sentence)		#(....,x,...)
	sentence = re.sub(r','+argToReplace+'\)', ','+newValue+')', sentence)	#(....,x)
	return sentence

#sentenceFromKB and current CS Sentence should not have any variable with the same name
def performStandardization(sentenceFromKB, currentSentences, literalFromKB):
	kbLiterals = sentenceFromKB.split('|')
	csLiterals = currentSentences.split('|')
	uniqKBVarArguments = getVariableArgumentList(kbLiterals)	#contains all the variables in KB sentence
	uniqCSVarArguments = getVariableArgumentList(csLiterals)	#contains all the variables in CS sentence
	commonVars = filter(lambda x: x in uniqCSVarArguments, uniqKBVarArguments)
	#replace the common Variable in KB sentence to something that is not in both CS and KB
	for var in commonVars:
		newVariable = getNewVariable(uniqKBVarArguments, uniqCSVarArguments)
		uniqKBVarArguments.remove(var)			#because we are replacing the common var only in KB sentence
		uniqKBVarArguments.append(newVariable)
		sentenceFromKB = replaceArgumentInSentence(var, newVariable, sentenceFromKB)
		literalFromKB = replaceArgumentInSentence(var, newVariable, literalFromKB)
	return {'literalFromKB':literalFromKB, 'sentenceFromKB':sentenceFromKB}

def resolveTheSentences(sentenceFromKB, currentSentences, literalFromCS, literalFromKB):
	newCS = ''
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

#unify the max 100 arguments and resolve the sentences
#literalToUnify will be in currentSentences
def unifyAndResolve(sentenceFromKB, currentSentences, literalFromCS, literalFromKB):
	#print "Here to unify : "+sentenceFromKB+" and "+currentSentences
	#print "Literal from CS : "+literalFromCS+" :: literal from KB : "+literalFromKB
	standardizedKBArguments = performStandardization(sentenceFromKB, currentSentences, literalFromKB)
	literalFromKB = standardizedKBArguments['literalFromKB']
	sentenceFromKB = standardizedKBArguments['sentenceFromKB']
	argumentsFromCS = literalFromCS.split('(')[1].rstrip(')')
	argumentsFromKB = literalFromKB.split('(')[1].rstrip(')')
	unificationValues = unify(argumentsFromCS, argumentsFromKB)
	#print "KB Arguments : "+argumentsFromKB+" :: CS Arguments : "+argumentsFromCS+" :: Unification Values : "+str(unificationValues)
	if unificationValues is None:
		return None
	for item in unificationValues['forKB']:
		sentenceFromKB = replaceArgumentInSentence(item, unificationValues['forKB'][item], sentenceFromKB)
		literalFromKB = replaceArgumentInSentence(item, unificationValues['forKB'][item], literalFromKB)
	for item in unificationValues['forCS']:
		currentSentences = replaceArgumentInSentence(item, unificationValues['forCS'][item], currentSentences)
		literalFromCS = replaceArgumentInSentence(item, unificationValues['forCS'][item], literalFromCS)
	#print "Updated KB sentence : "+sentenceFromKB+" :: Updated CS sentence : "+currentSentences
	newCS = resolveTheSentences(sentenceFromKB, currentSentences, literalFromCS, literalFromKB)
	return newCS

def getLiteralSignature(literal):
	literalParts = literal.split('(')
	signature = literalParts[0]+'('
	literalArgs = literalParts[1].rstrip(')').split(',')
	for arg in literalArgs:
		if len(arg) == 1 and re.match(r'[a-z]', arg):
			signature+='v,'
		else:
			signature+=arg+','
	signature+=')'
	return signature

def isLiteralBeingUnified(literal):
	global csLiteralBeingUnified
	litType = getLiteralSignature(literal)
	if litType in csLiteralBeingUnified:
		return True
	return False

def addLiteralToBeingUnified(literal):
	global csLiteralBeingUnified
	litType = getLiteralSignature(literal)
	csLiteralBeingUnified[litType] = 1

def removeLiteralFromBeingUnified(literal):
	global csLiteralBeingUnified
	litType = getLiteralSignature(literal)
	if litType in csLiteralBeingUnified:
		del csLiteralBeingUnified[litType]

def findResolution(currentSentences):
	#print "\nCurrent Sentence : "+currentSentences
	global KBIndexes, KBSentences, literalsThatCannotBeUnified
	if currentSentences == 'contradiction':
		return True
	else:
		addCSToVisitiedSentences(currentSentences)
	csLiterals = currentSentences.split('|')
	csLiterals = list(set(csLiterals))
	currentSentences = '|'.join(csLiterals)
	#print "CS Literals : "+str(csLiterals)
	for literal in csLiterals:
		#check if cs literal is currently in the process of being unified
		if isLiteralBeingUnified(literal):
			#print "Continuing because "+literal+" is already being unified"
			continue
		negatedLiteral = getNegationOfLiteral(literal)
		predicateNegatedLiteral = negatedLiteral.split('(')[0]
		linesToUnifyWithCS = []
		if predicateNegatedLiteral in KBIndexes:
			linesToUnifyWithCS = KBIndexes[predicateNegatedLiteral]
		#print literal+" can be resolved with lines : "+str(linesToUnifyWithCS)
		#add the CS literal being unified
		addLiteralToBeingUnified(literal)
		for line in linesToUnifyWithCS:
			#line can have multiple predicates that can unify the current literal
			kbLiterals = KBSentences[line].split('|')
			for kbLiteral in kbLiterals:
				if kbLiteral.split('(')[0] == predicateNegatedLiteral and (literal not in literalsThatCannotBeUnified or str(line)+'_'+kbLiteral not in literalsThatCannotBeUnified[literal]):
					newCS = unifyAndResolve(KBSentences[line], currentSentences, literal, kbLiteral)
					#print "Unified "+currentSentences+" with "+str(KBSentences[line])+" to get : "+str(newCS)
					if newCS is None:		#this condition is true when the sentences fail to unify and resolve
						if not literal in literalsThatCannotBeUnified:
							literalsThatCannotBeUnified[literal] = []
						literalsThatCannotBeUnified[literal].append(str(line)+'_'+kbLiteral)
						continue
					if not isNewCSInVisitedSentences(newCS) and findResolution(newCS):
						return True
		#remove the CS Literal being unified
		removeLiteralFromBeingUnified(literal)
	#add the current CS to the list of non unified sentences
	return False

def checkQueries(queries):
	global KBSentences, KBIndexes, visitedSentences, csLiteralBeingUnified, literalsThatCannotBeUnified
	outputs = []
	for q in queries:
		q = re.sub(' ','',q)
		q = re.sub('\t','',q)
		visitedSentences = {}
		csLiteralBeingUnified = {}
		literalsThatCannotBeUnified = {}
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
		#print KBSentences
		#print KBIndexes
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
		#print "Parsing : "+s
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
	#print (fileData)
	#testCNFConversion()
	populateKB(fileData['sentences'])
	output = checkQueries(fileData['queries'])
	print output
	createOutputFile(output)

main()

=======
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:10:12 2019

@author: Carson
"""
import re
import os
import csv
  
CMD   = re.compile("[OPEN|CLOSE|WRITE|EXIT|SHOW|CREATE|UPDATE|INSERT|DELETE]")
class Lexer(object):
    # Removes the first and last "end" characters in a string, or values in an array.
    def remove_parenthesis(self, line, end):
        line[0]  = line[0][1:]            # Remove the left parenthesis
        line[-1] = line[-1][:-end]        # Remove the right side
        
    # Given a schema rule and a value, check if the rule is being followed.
    def check_schema(self, schema, value):
        # VARCHAR case
        if schema.split("(")[0].lower() == "varchar":
            # Check if the length of the character string abides by the schema
            if len(value) > int(schema.split("(")[1].replace(")", "")):
                return False # TOO LARGE!
            else:
                return True  # Works.
        # Integer case
        else:
            if value.isdigit():
                return True  # Is an integer.
            else:
                return False # Is some junk.
             
    # Returns the index of the operator to split expression into left and right components
    def getAtom(self, line):
    	index = -1
    	# If there are parenthesis, find the end of them
    	# This is the first atomic expression
    	if line[0] == '(':
    		count = 1
    		index = 1
    		while count > 0:
    			if line[index] == '(':
    				count += 1
    			if line[index] == ')':
    				count -= 1
    			index += 1
    		index += 1
    	# The first atomic expression is a relation name, so return whichever operator is first in the string
    	else:
    		for c in line:
    			index += 1
    			if (c == '+') | (c == '-') | (c == '*') | (c == '&'):
    				break
    	return index
    
    # Evaluates an expression
    def evaluateExpr(self, line):
        line = " ".join(line).replace(";","").split(" ")
        expr = line[0]	# Either holds a command or the beginning of a relation

        # Make a temporary table with a unique name
        tmp_name = "tmp1"
        i = 1
        while tmp_name in self.tables.keys():
        	i += 1
        	tmp_name = "tmp" + str(i)
        self.tables[tmp_name] = {}
        self.schemas[tmp_name] = {}
        self.primary_keys[tmp_name] = {}

        # Handle projections
        if expr == "project":
        	# Get attribute list
            i = 1
            while True:
                if line[i][-1] == ')':
                    i += 1
                    break
                i += 1

            attr_lst = line[1:i]
            # Remove commas and parenthsis
            attr_lst[0] = attr_lst[0][1:]
            attr_lst[-1] = attr_lst[-1][:-1]
            attr_lst = " ".join(attr_lst).replace(",", "")
            attr_lst = attr_lst.split(" ")
            # Evaluate atomic expression
            atom = line[i:]
            atom = self.evaluateAtomic(atom)

            # Get list of attribute types
            type_lst = []
            for atr, typ in zip(self.schemas[atom]["attributes"], self.schemas[atom]["types"]):
            	if atr in attr_lst:
            		type_lst.append(typ)

            self.schemas[tmp_name]["attributes"] = attr_lst
            self.schemas[tmp_name]["types"] = type_lst
            self.primary_keys[tmp_name] = attr_lst

            # Check if source is a table
            if not atom in self.tables.keys():
                print("ERROR! Source table does not exist")
                return

            # Make sure attributes match
            for attr in attr_lst:
                if not attr in self.schemas[atom]["attributes"]:
                    print("ERROR! Attribute", attr, "does not exist")
                    return
            
            # Write dummy insert request containing entry info to pass to insert
            for row in self.tables[atom]:
                dummy_line = [' ']*(5+len(attr_lst))
                dummy_line[2] = tmp_name
                i = 5
                for attr in attr_lst:
            	    dummy_line[i] = self.tables[atom][row][attr]
            	    i = i+1

                dummy_line[5] = "(\"" + dummy_line[5]
                dummy_line[-1] = dummy_line[-1] + ");"
                self.insert(dummy_line)

            return tmp_name
        # Handle selections
        elif expr == "select":
        	sel = " ".join(line)
        	count = 0
        	index = 0
        	for c in sel:
        		index += 1
        		if c == '(':
        			count += 1
        		if c == ')':
        			count -= 1
        			if (count == 0) & (c != sel[0]):
        				break

        	# Evaluates atomic expression and returns temp table name holding relation
        	atom = sel[index+1:len(sel)].split(" ")
        	index = -1
        	for word in line:
        		index += 1
        		if word == atom[0]:
        			break

        	atom = self.evaluateAtomic(atom)

        	# Make a dummy line for fake select request to call select funtion
        	dummy_line = [' ']*(4+(index-1))
        	dummy_line[0] = tmp_name
        	dummy_line[1] = '<-'
        	dummy_line[2] = 'select'
        	for i in range(1,index):
        		dummy_line[i+2] = line[i]
        	dummy_line[-1] = atom

        	# Call select to fill up temp table to return
        	self.select(dummy_line)

        	return tmp_name
        # Handle renaming
        elif expr == "rename":
        	# Get attribute list
            i = 1
            while True:
                if line[i][-1] == ')':
                    i += 1
                    break
                i += 1

            attr_lst = line[1:i]
            # Remove commas and parenthsis
            attr_lst[0] = attr_lst[0][1:]
            attr_lst[-1] = attr_lst[-1][:-1]
            attr_lst = " ".join(attr_lst).replace(",", "")
            attr_lst = attr_lst.split(" ")
            # Evaluate atomic expression
            atom = line[i:]
            atom = self.evaluateAtomic(atom)

            # Check if source is a table
            if atom not in self.tables.keys():
                print("ERROR! Source table does not exist")
                return

            self.schemas[tmp_name]["attributes"] = attr_lst
            self.primary_keys[tmp_name] = attr_lst

            if len(self.schemas[atom]["attributes"]) != len(self.schemas[tmp_name]["attributes"]):
            	print("ERROR! Number of attributes don't match")
            	return

             # Get list of attribute types
            type_lst = []
            for atr, typ in zip(self.schemas[tmp_name]["attributes"], self.schemas[atom]["types"]):
            	if atr in attr_lst:
            		type_lst.append(typ)
            self.schemas[tmp_name]["types"] = type_lst

            # Write dummy insert request containing entry info to pass to insert
            for row in self.tables[atom]:
                dummy_line = [' ']*(5+len(attr_lst))
                dummy_line[2] = tmp_name
                i = 5
                for attr in self.schemas[atom]["attributes"]:
            	    dummy_line[i] = self.tables[atom][row][attr]
            	    i = i+1

                dummy_line[5] = "(\"" + dummy_line[5]
                dummy_line[-1] = dummy_line[-1] + ");"
                self.insert(dummy_line)

            return tmp_name
        # Handle Relational Algebra
        elif ('+' in line) | ('-' in line) | ('*' in line) | ('&' in line):
        	line = " ".join(line)
        	i = self.getAtom(line)	# Returns the index of the operator
        	# Split into left and right sides
        	left = line[0:i-1]
        	right = line[i+2:len(line)]
        	#Evaluate each atomic expression and return their temp table names
        	lname = self.evaluateAtomic(left.split(" "))
        	rname = self.evaluateAtomic(right.split(" "))

            # Handle Union
        	if line[i] == '+':
        		# Check if relation is union compatible
	            if len(self.schemas[lname]["attributes"]) != len(self.schemas[rname]["attributes"]):
	                for types in self.schemas[lname]["types"]:
	                	if types not in self.schemas[rname]["types"]:
	                	    print("ERROR! Relation is not union compatible")
	                	    return tmp_name

	            # Fill attributes, types, and keys
	            self.schemas[tmp_name]["attributes"] = self.schemas[lname]["attributes"]
	            self.schemas[tmp_name]["types"] = self.schemas[lname]["types"]
	            self.primary_keys[tmp_name] = self.primary_keys[lname]

	            # Add first table
	            for row in self.tables[lname]:
	            	dummy_line = [' ']*(5+len(self.schemas[lname]["attributes"]))
	            	dummy_line[2] = tmp_name
	            	i = 5
	            	for attr in self.schemas[lname]["attributes"]:
	            	    dummy_line[i] = self.tables[lname][row][attr]
	            	    i = i+1

	            	dummy_line[5] = "(\"" + dummy_line[5]
	            	dummy_line[-1] = dummy_line[-1] + ");"
	            	self.insert(dummy_line)

	            # Append second table
	            for row in self.tables[rname]:
	            	dummy_line = [' ']*(5+len(self.schemas[rname]["attributes"]))
	            	dummy_line[2] = tmp_name
	            	i = 5
	            	for attr in self.schemas[rname]["attributes"]:
	            	    dummy_line[i] = self.tables[rname][row][attr]
	            	    i = i+1

	            	dummy_line[5] = "(\"" + dummy_line[5]
	            	dummy_line[-1] = dummy_line[-1] + ");"
	            	self.insert(dummy_line)

	            return tmp_name	# Holds name of tmp table
	        # Handle Difference
        	elif line[i] == '-':
        		# Check if relation is union compatible
	            if len(self.schemas[lname]["attributes"]) != len(self.schemas[rname]["attributes"]):
	                for types in self.schemas[lname]["types"]:
	                	if types not in self.schemas[rname]["types"]:
	                	    print("ERROR! Relation is not union compatible")
	                	    return tmp_name

	            # Fill attributes, types, and keys
	            self.schemas[tmp_name]["attributes"] = self.schemas[lname]["attributes"]
	            self.schemas[tmp_name]["types"] = self.schemas[lname]["types"]
	            self.primary_keys[tmp_name] = self.primary_keys[lname]

	            # List to manipulate to hold every tuple in the difference
	            entries = []
	            # Add left side of the expression
	            for row in self.tables[lname]:
	            	i = 0
	            	entry = [' ']*(len(self.schemas[lname]["attributes"]))
	            	for attr in self.schemas[lname]["attributes"]:
	            	    entry[i] = self.tables[lname][row][attr]
	            	    i = i+1
	            	entries.append(entry)

	            for row in self.tables[rname]:
	            	i = 0
	            	entry = [' ']*(len(self.schemas[lname]["attributes"]))
	            	for attr in self.schemas[rname]["attributes"]:
	            	    entry[i] = self.tables[rname][row][attr]
	            	    i = i+1
	            	if entry in entries:
	            		entries.remove(entry)

	            for entry in entries:
	            	dummy_line = [' ']*(5+len(entry))
	            	dummy_line[2] = tmp_name
	            	i = 0
	            	for attr in self.schemas[rname]["attributes"]:
	            	    dummy_line[i+5] = entry[i]
	            	    i = i+1

	            	dummy_line[5] = "(\"" + dummy_line[5]
	            	dummy_line[-1] = dummy_line[-1] + ");"
	            	self.insert(dummy_line)

	            return tmp_name
        	# Handle Product
        	elif line[i] == '*':
        		# Get list of attributes
        	    attr_lst = []
	            for attr in self.schemas[lname]["attributes"]:
	            	attr_lst.append(attr)
	            for attr in self.schemas[rname]["attributes"]:
	            	attr_lst.append(attr)
	            self.schemas[tmp_name]["attributes"] = attr_lst
	            self.primary_keys[tmp_name] = attr_lst

	            # Get list of types
	            type_lst = []
	            for t in self.schemas[lname]["types"]:
	            	type_lst.append(t)
	            for t in self.schemas[rname]["types"]:
	            	type_lst.append(t)
	            self.schemas[tmp_name]["types"] = type_lst

	            # Iterature through tuples and implement product
	            for row in self.tables[lname]:
	            	pre = []
	            	for attr in self.schemas[lname]["attributes"]:
	            		pre.append(self.tables[lname][row][attr])
	            	for r in self.tables[rname]:
	            		app = []
		            	for attr in self.schemas[rname]["attributes"]:
		            		app.append(self.tables[rname][r][attr])
		            	new_tuple = pre + app

		            	dummy_line = [' ', ' ', tmp_name, ' ', ' ']
		            	dummy_line[2] = tmp_name
		            	dummy_line = dummy_line + new_tuple
		            	dummy_line[5] = "(\"" + dummy_line[5]
		            	dummy_line[-1] = dummy_line[-1] + ");"
		            	self.insert(dummy_line)

	            return tmp_name
        	# Handle Natural Join
        	elif line[i] == '&':
        		# Find common attributes
        		attr_lst = []
        		for attr in self.schemas[lname]["attributes"]:
        			if attr in self.schemas[rname]["attributes"]:
        				attr_lst.append(attr)

        		# Get list of attributes and types
        		attrs = []
        		types = []
        		for a, t in zip(self.schemas[lname]["attributes"], self.schemas[lname]["types"]):
        			attrs.append(a)
        			types.append(t)
        		for a, t in zip(self.schemas[rname]["attributes"], self.schemas[rname]["types"]):
        			if a not in attr_lst:
        				attrs.append(a)
        				types.append(t)
        		self.schemas[tmp_name]["attributes"] = attrs
        		self.schemas[tmp_name]["types"] = types
        		self.primary_keys[tmp_name] = attrs

        		# Iterate through tuples and implement natural join
        		for row in self.tables[lname]:
        			for row2 in self.tables[rname]:
        				match = True
        				for attr in attr_lst:
        					match = match & (self.tables[lname][row][attr] == self.tables[rname][row2][attr])
        				if match:
        					new_tuple = []
        					for a in self.schemas[lname]["attributes"]:
        						new_tuple.append(self.tables[lname][row][a])
        					for a in self.schemas[rname]["attributes"]:
        						if a not in attr_lst:
        							new_tuple.append(self.tables[rname][row2][a])
        					# Insert dummy line
        					dummy_line = [' ', ' ', tmp_name, ' ', ' ']
        					dummy_line[2] = tmp_name
        					dummy_line = dummy_line + new_tuple
        					dummy_line[5] = "(\"" + dummy_line[5]
        					dummy_line[-1] = dummy_line[-1] + ");"
        					self.insert(dummy_line)

        		return tmp_name
            
        # Handle atomic expression
        else:
        	return self.evaluateAtomic(line)

    # Evaluates an atomic expression
    def evaluateAtomic(self, line):
        line = " ".join(line).replace(";","")
        # First case of ( expr )
        if '(' in line:
            line = line[1:len(line)-1]
            line = line.split(" ")
            return self.evaluateExpr(line)
        # Case for relation name
        else:
        	return line
        
	# Parses a relational query
    def relational(self, line):
    	# Get basic info from line
        expr = line[6:]
        table = line[2]

        # Evaluate the relation
        name = self.evaluateExpr(expr)	# Name of the temporary table that has the solution

        # Copy table from temporary table by writing dummy insert requests
        for row in self.tables[name]:
            dummy_line = [' ']*(5+len(self.schemas[name]["attributes"]))
            dummy_line[2] = table
            i = 5
            for attr in self.schemas[name]["attributes"]:
            	dummy_line[i] = self.tables[name][row][attr]
            	i += 1

            dummy_line[5] = "(\"" + dummy_line[5]
            dummy_line[-1] = dummy_line[-1] + ");"
            self.insert(dummy_line)

        return

    # Evaluates condition in simple form of "operand operator operand"
    def evaluateCondition(self, condition, tableToCheckFrom, tableEntry) :
        
        entryAttrib = self.tables[tableToCheckFrom][tableEntry][condition[0]]

        # determines if we're comparing a string literal or a number
        isNumber = False
        originalCommand = condition[2]

        # Removes quotations from the string literal, need be, and also converts to number if needed (only works for ints, due to .isdigit)
        if type(condition[2]) != float:
            for x in range(len(condition)):
                condition[x] = condition[x].replace('\"','')
            if condition[2].isdigit():
                condition[2] = float(condition[2])

        # if nothing changed, then there were no quotes and we have a number (might have to check whether to cast to int or float?)
        if entryAttrib.isdigit():
            entryAttrib = float(entryAttrib)

        if condition[1] == "==" :
            if entryAttrib == condition[2]:
                return True
        elif condition[1] == "!=" :
            if entryAttrib != condition[2]:
                return True
        elif condition[1] == "<" :
            if entryAttrib < condition[2]:
                return True
        elif condition[1] == ">" :
            if entryAttrib > condition[2]:
                return True
        elif condition[1] == "<=" :
            if entryAttrib <= condition[2]:
                return True
        elif condition[1] == ">=" :
            if entryAttrib >= condition[2]:
                return True
        return False

    # Name is self explanitory
    def findIndexOfCloseParenthesis(self, indexesWithCloseParenthesisList, openParenthesisIndex):
        if len(indexesWithCloseParenthesisList) == 0: # returns -1, as this will not naturally occur
            return -1

        indexesAfterOpen = []
        for index in indexesWithCloseParenthesisList:
            if index > openParenthesisIndex:
                indexesAfterOpen.append(index)

        return min(indexesAfterOpen)

    # returns a bool, takes in something like (thing to check <operator> thing to check against), possibly more
    # with || or && in between, but only one level of parentheses
    def processInnerCommands(self, commands, tableToCheckFrom, tableEntry):

        singleEvaluation = False

        if len(commands) <= 3:
            singleEvaluation = True

        commandsToProcess = commands.copy() # copy to not mutate data

        # remove parentheses
        for token in range(len(commandsToProcess)):
            if type(commandsToProcess[token]) != bool:
                commandsToProcess[token] = commands[token].replace('(','').replace(')','')
            if commandsToProcess[token] == '': # used to protect against tokens that are just parentheses
                commandsToProcess = commandsToProcess[:token]
                break

        if not singleEvaluation:
            i = 0
            # go through and evaluate the strings of 3 items to true or false
            for token in commandsToProcess:
                if token == "&&" or token == "||":
                    if type(commandsToProcess[i-1]) != bool and type(commandsToProcess[i-3]) != bool: # if it is a bool, I don't need to change it right now
                        # evaluate the string of three things and replace with output bool
                        boolResult = self.evaluateCondition(commandsToProcess[i-3:i], tableToCheckFrom, tableEntry)
                        commandsToProcess[i-3] = boolResult
                i += 1

            # Evaluate the last condition, need be
            if type(commandsToProcess[i-1]) != bool:
                boolResult = self.evaluateCondition(commandsToProcess[i-3:i], tableToCheckFrom, tableEntry)
                commandsToProcess[i-3] = boolResult
        else:
            commandsToProcess[0] = self.evaluateCondition(commandsToProcess, tableToCheckFrom, tableEntry)

        # Gets rid of all the data we no longer need in the commands (so not bools or &&/||)
        for token in commandsToProcess:
            if type(token) != bool and token != "&&" and token != "||":
                commandsToProcess.pop(commandsToProcess.index(token))

        # The current T/F state of the line from left to right
        boolStateFromLeft = commandsToProcess[0]

        # We now have the commands in the form of something like "True || False && True"
        for token in commandsToProcess:
            if token == "&&":
                boolStateFromLeft = (boolStateFromLeft and commandsToProcess[commandsToProcess.index(token) + 1])
            elif token == "||":
                boolStateFromLeft = (boolStateFromLeft or commandsToProcess[commandsToProcess.index(token) + 1])

        return boolStateFromLeft


    # Does what select should do, takes the name of the table to insert to (use a temp val need be) and the
    # set of select commands in particular (so like "select (kind == "cat") animals" and things of that simple nature)
    # Must remove (outer) parentheses beforehand, table to search from must be last element in selectBlock (so "animals" in above)
    # TODO IMPORTANT: Call THIS function when you need to process just a select block, for example, the line
    # common_names <- project (name) (select (aname == name && akind != kind) (a * animals));
    # You would get just the "select (aname == name && akind != kind) 'tablename'" part, and pass that into THIS function
    # This function does not currently have the capability of resolving "a * animals" to a table, I feel like doing that
    # first and replacing that part of the table with the new table name would be the best course of action
    def processSelectBlock(self, tableToInsertTo, selectBlock, tableToCheckFrom):
        # This should contain only the commands to parse (parentheses included)
        commandsOriginal = selectBlock.copy()

        # Find where the parentheses are
        i = 0
        indexesWithOpenParenthesisOriginal = []
        indexesWithCloseParenthesisOriginal = []
        for item in commandsOriginal:
            if type(item) != bool and len(item) >= 2:
                if item[0] == "(":
                    indexesWithOpenParenthesisOriginal.append(i)
                if item[-1] == ")":
                    indexesWithCloseParenthesisOriginal.append(i)
            i += 1
        # This replaces all of the commands to something like "True && False || True" in the correct order
        for tableEntry in self.tables[tableToCheckFrom]:
            commands = commandsOriginal.copy()
            indexesWithOpenParenthesis = indexesWithOpenParenthesisOriginal.copy()
            indexesWithCloseParenthesis = indexesWithCloseParenthesisOriginal.copy()
            # replaces the list of commands with all true and false values
            while len(indexesWithOpenParenthesis) > 0 or len(indexesWithCloseParenthesis) > 0:
                closeParenthesisIndex = self.findIndexOfCloseParenthesis(indexesWithCloseParenthesis, max(indexesWithOpenParenthesis))
                # if no close parentheses, then do the rest of the line from the last open
                if closeParenthesisIndex == -1:
                    innerCommandResult = self.processInnerCommands(commands[max(indexesWithOpenParenthesis):], tableToCheckFrom, tableEntry)
                else:
                    innerCommandResult = self.processInnerCommands(commands[max(indexesWithOpenParenthesis):closeParenthesisIndex + 1], tableToCheckFrom, tableEntry)
                # Replaces the open token with a bool
                commands[max(indexesWithOpenParenthesis)] = innerCommandResult
                # Gets rid of the other elements I no longer need, this also auto removes parentheses (deletes rest of block that didn't turn to bool)
                indexingVar = max(indexesWithOpenParenthesis) + 1
                while indexingVar <= closeParenthesisIndex:
                    commands.pop(max(indexesWithOpenParenthesis) + 1) #since you keep popping, you need to keep popping the same index
                    indexingVar += 1
                indexesWithOpenParenthesis.pop(indexesWithOpenParenthesis.index(max(indexesWithOpenParenthesis)))
                # Used because sometimes (when a token is like "thing))") the index is -1 to indicate that there is no index with a cp
                if closeParenthesisIndex != -1:
                    indexesWithCloseParenthesis.pop(indexesWithCloseParenthesis.index(closeParenthesisIndex))
            # Same logic as inner commands, just final check
            boolStateFromLeft = commands[0]
            for token in commands:
                if token == "&&":
                    boolStateFromLeft = (boolStateFromLeft and commands[commands.index(token) + 1])
                elif token == "||":
                    boolStateFromLeft = (boolStateFromLeft or commands[commands.index(token) + 1])
            # Insert if statement evaluated true
            if boolStateFromLeft:
                self.tables[tableToInsertTo][tableEntry] = self.tables[tableToCheckFrom][tableEntry]

    # Given knowledge of primary keys, the attibutes of a row, and the values,
    # generate a primary key. Usage of ord() simply transfers characters into
    # their ASCII values, and generates a key.
    def generate_key(self, key_rules, attributes, values):
        key = 0
        for i in range(len(attributes)):
            # Check if a given variable is a primary key
            if attributes[i] in key_rules:
                # Check if that variable is a string, if so, use ord()
                if not key_rules[i].isdigit():
                    for char in values[i]:
                        key = key + ord(char)
                # Otherwise, add the literal integer value of the key.
                else:
                    key = key + int(values[i])
                    
        # Return the generated key.
        return int(key)
        
    # Opens a table from disk.
    def _open(self, line):
        # Generate the filename to open.
        tablename = ""
        filename  = ""
        if ".csv" not in line[1].lower():
            filename  = line[1][:-1] + ".csv"
            tablename = line[1][:-1]
        else:
            filename  = line[1][:-1]
            tablename = line[1][:-4]
            
        # Make sure this table isn't in memory so nothing is overwritten.
        if tablename in self.tables.keys():
            print("ERROR! Attempting to OPEN a table currently in memory: " + str(tablename) + "!")
            return
            
        # Grab the location of the current working directory, build the path.
        __location__  = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file_location = os.path.join(__location__, filename)
        
        # Check if the file exists
        if not os.path.exists(file_location):
            print("ERROR! Attempting to open a null file: " + str(filename) + "!")
            return

        # Open the file, begin populating the table.
        line_count = 0
        self.tables[tablename] = {}
        with open(file_location)  as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            variables  = []
            types      = []
            for row in csv_reader:
                if line_count == 0:
                    # Parse primary keys
                    self.primary_keys[tablename] = \
                    (" ".join(row[0].split(" ")[1:])[1:-1]).split(" ")
                    # Parse variables, schema
                    for item in row[1:]:
                        var_data   = item.split(" ")
                        var_name   = var_data[0]
                        var_schema = var_data[1]
                        variables.append(var_name)
                        types.append(var_schema)
                else:
                    # Insert the key for the given row, and create the data structure.
                    self.tables[tablename][row[0]] = {}
                    
                    # Insert the variables into the key.
                    for i in range(1, len(row)):
                        self.tables[tablename][row[0]][variables[i - 1]] = row[i] 
                line_count += 1
            self.schemas[tablename] = types
        print(self.tables[tablename])
                        
    # Closes the given table, and removes it from the table dictionary.
    def close(self, line):
        # Removes the ';' after table name:
        table = line[1][:-1].lower() 
        
        # Check if the table exists, and is currently open.
        if table not in self.tables.keys() or table not in self.files.keys():
            print("ERROR! Attempting to close a null file: " + str(table) + ".csv!")
            return
        # If it exists and is open, close the file and remove the record from memory.
        self.files[table].close()
        self.tables.pop(table)
        self.files.pop(table)
        self.schemas.pop(table)
        self.primary_keys.pop(table)
        
    # Writes the given table to disk.
    def write(self, line):
        # Removes the ';' after table name:
        table = line[1][:-1].lower()
        
        # Check if the table exists.
        if table not in self.tables.keys():
            print("ERROR! Attempting to write a null table: " + str(table) + "!")
            return
        
        # Write the table into a CSV formatted file.
        filename = str(table) + ".csv"
        with open(filename, 'w') as f:
            # Save a pointer to this output file.
            self.files[table] = f                
            
            # Pairs variable names with variable types for reopening tables later.
            names  = map(" ".join ,zip(self.schemas[table]["attributes"], self.schemas[table]["types"]))
            
            # Writes this header to the file, keeping the primary key generation rules with the ID.
            header = ",".join(names)
            f.write("id (%s),%s\n"%(" ".join(self.primary_keys[table]), header))
            
            # Writes rows of data to the CSV file.
            for row in self.tables[table].keys():
                # Parse the variables in-order so that they appear on correct columns.
                variables = []
                for variable in self.schemas[table]["attributes"]:
                    variables.append(self.tables[table][row][variable])
                    
                # Format the row and write it to the CSV.
                var = ",".join(variables)
                f.write("%s,%s\n"%(row, var))
        
    # Checks if the requested table exists
    def show(self, line):
        table_name = line[1][:-1]
        if table_name not in self.tables.keys():
            print("ERROR! Attempted to display a null table: " + str(table_name) + "!")
            return
        
        # Shows the given table in a formatted manner.
        print("\n~~~~~~~~~~~~<" + str(table_name) + ">~~~~~~~~~~~")
        table = self.tables[table_name]
        for key in table:
            print(str(table[key]))
        print("~~~~~~~~~~~~</" + str(table_name) + ">~~~~~~~~~~\n")
        
    # Creates a table
    def create(self, line):
         # Make sure the requested table name isn't in use.
        new_name               = line[2]
        if new_name in self.tables.keys():
            print("ERROR! Attempted to overwrite an existing table: " + str(new_name) + "!")
            return
        self.tables[new_name]  = {}     # Creates a name-indexable dictionary to serve as the new table.
        self.schemas[new_name] = {}     # Creates a table for quick access to schema rules.
        
        # Parse the schema
        i = 3                                                 # Schema begins on 4th item.
        while line[i].lower() != "primary":                   # Count schema directives.
            i = i + 1
        schema = line[3:i]                                    # Grab the schema section of the array.
        schema = " ".join(schema).replace(",", "").split(" ") # Remove commas.
        self.remove_parenthesis(schema, 1)                    # Removes the paranthesis syntax.
        
        # Make the schema check O(1)  schemas <database><variable> = <Varchar(*)>
        attributes = []
        types      = []
        for x in range(0, len(schema), 2):
            attributes.append(schema[x])
            types.append(schema[x + 1])
        self.schemas[new_name]["attributes"] = attributes
        self.schemas[new_name]["types"]      = types
        
        # Setup primary keys
        keys = line[i + 2:]                                  # Grab the primary keys
        keys = " ".join(keys).replace(",", "").split(" ")    # Remove commas.
        self.remove_parenthesis(keys, 2)                     # Removes the paranthesis syntax.
        
        # Add the primary keys to the table.
        self.primary_keys[new_name] = keys                   # Sets up keys to the table.
        
    # Updates some set of the values that matches a criterion to a given value.
    def update(self, line):
        print("UPDATE")
        
     # Inserting values into a table
    def insert(self, line):
        table_name = line[2]
        if table_name not in self.tables.keys():
            print("ERROR! Attempting to insert into a null table: " + str(table_name) + "!")
            return
        
        # Handle relational queries
        if line[5] == "RELATION":
        	# Solve relation
            self.relational(line)

            # Clean up temporary tables
            entries = []
            for entry in self.tables.keys():
            	if "tmp" in entry:
            		entries.append(entry)
            for entry in entries:
            	del self.tables[entry]
            	del self.schemas[entry]
            	del self.primary_keys[entry]
        else:
            # Grab the values to be inserted
            values = line[5:]
            values = " ".join(values).replace(",", "")
            values = values.replace("\"", "").split(" ")
            self.remove_parenthesis(values, 2)
            
            # Check the schema fit of the values.
            schema = self.schemas[table_name]
            
            # Iterate over the attributes being inserted
            for i in range(len(schema["attributes"])):
                # Check if the given variables fit this table's schema
                if not self.check_schema(schema["types"][i], values[i]):
                    print("ERROR! Schema violation! Insertion aborted.")
                    return
            
            # Create a unique key
            key_rules   = self.primary_keys[table_name]
            primary_key = self.generate_key(key_rules, schema["attributes"], values)
            
            # Check if the generated key is unique
            if primary_key in self.tables[table_name].keys():
                print("ERROR! Primary key violation! Non-unique key result")
                return
            
            # Create the record
            self.tables[table_name][primary_key] = {}
            
            # Insert the data into the record, indexed by variable name.
            for varname, val in zip(self.schemas[table_name]["attributes"], values):
                self.tables[table_name][primary_key][varname] = val
    
    # Delete from a table some subset that matches a condition.
    def delete(self, line):
        print("TODO! DELETE")

    # Select some subset of the table
    # This should only be called for a full line with only a select call, like
    # dogs <- select (kind == "dog") animals;
    def select(self, line):
        # make lists of the conditions we need to evaluate
        conditionListAnd = []
        conditionListOr = []

        # since we're making a new table, this makes sure it doesn't exist yet
        if line[0].lower() in self.tables.keys():
            print("Error, table already exists")
            return
        
        # sets up the new table
        self.tables[line[0].lower()] = {}  
        # Passes to helper function to actually fill with correct elements
        self.processSelectBlock(line[0].lower(), line[3:-1], line[-1][:-1]) # last split is to get rid of semicolon

        print("\n~~~~~~~~~~~~<" + line[0].lower() + ">~~~~~~~~~~~")
        table = self.tables[line[0].lower()]
        for key in table:
            print(str(table[key]))
        print("~~~~~~~~~~~~</" + str(line[0].lower()) + ">~~~~~~~~~~\n")

    # ion
    def project(self, line):
        print("TODO! PROJECT")
        
    # Renames a table
    def rename(self, line):
        print("TODO! RENAME")

    # Evaluates an atomic expression
    def evaluateAtomic(self, line):
        line = " ".join(line).replace(";","")
        if '(' in line:
            line = line[1:len(line)-1]
            line = line.split(" ")
            return self.evaluateExpr(line)
        else:
        	return line
        
		# Parses a relational query
    def relational(self, line):
    	# Get basic info from line
        expr = line[6:]
        table = line[2]

        # Evaluate the relation
        name = self.evaluateExpr(expr)	# Name of the temporary table that has the solution

        # Copy table from temporary table by writing dummy insert requests
        for row in self.tables[name]:
            dummy_line = [' ']*(5+len(self.schemas[name]["attributes"]))
            dummy_line[2] = table
            i = 5
            for attr in self.schemas[name]["attributes"]:
            	dummy_line[i] = self.tables[name][row][attr]
            	i += 1

            dummy_line[5] = "(\"" + dummy_line[5]
            dummy_line[-1] = dummy_line[-1] + ");"
            self.insert(dummy_line)
        return 
        
    # Directs parse commands to their correct function.
    def parse_command(self, line):
        if line[0].lower() == "open"  : 
            self._open(line)
        if line[0].lower() == "close" : 
            self.close(line)      
        if line[0].lower() == "write" : 
            self.write(line)     
        if line[0].lower() == "show"  : 
            self.show(line)       
        if line[0].lower() == "create": 
            self.create(line)
        if line[0].lower() == "update": 
            self.update(line)       
        if line[0].lower() == "insert": 
            self.insert(line)        
        if line[0].lower() == "delete": 
            self.delete(line)
        if line[0].lower() == "exit"  : 
            return False   
        return True
        
    # Directs query commands to their correct function.
    def parse_query(self, line):
        if line[2].lower() == "select" : 
            self.select(line)     
        if line[2].lower() == "project": 
            self.project(line)       
        if line[2].lower() == "rename" : 
            self.rename(line)      
    
    # Constructor for the class, and where to put class variables.
    def __init__(self, filename):
        # In-memory representations of databases.
        self.files        = {}           # Holds a pointer to the files that have been opened for tables, indexed by table name.
        self.tables       = {}           # Holds in-memory representations of the tables, indexed by table name.
        self.schemas      = {}           # Holds the schema for tables in an array, indexed by table name.
        self.primary_keys = {}           # Holds the primary keys of the table, so that new records can be given new keys, indexed by table name.
        self.stream       = open(filename, "r")
        
        # Parses the file, line by line (command by command)
        for line in self.stream:
            line = line.replace("\n", "") # Remove \n
            line = line.replace("\r", "") # Remove \r
            arr  = line.split(" ")        # Split all lines on input
            
            # Skips empty space
            if len(arr) > 1:
                # If the line is a command...
                if CMD.match(arr[0], re.IGNORECASE):
                    
                    # Check for exit case
                    if not self.parse_command(arr):
                        # Exits on return of False
                        return
                    
                # If the line is a query...
                else:
                    self.parse_query(arr)
   
# Program start - can go into another file.     
def Main():
    # Opens the file "test.txt" from the current working directory.
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    lexicon = Lexer(os.path.join(__location__, 'test_alt.txt'))
    
Main() # Needed to make Main work.     
    
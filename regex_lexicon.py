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
        
        if line[5] == "RELATION":
            print("!!! TODO !!! Relational query insertion not implemented.")
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
    def select(self, line):
        print("TODO! SELECT")
        
    # Projection
    def project(self, line):
        print("TODO! PROJECT")
        
    # Renames a table
    def rename(self, line):
        print("TODO! RENAME")
        
    # Parses a relational query
    def relational(self, line):
        print("TODO! RELATIONAL")
        
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
        if line[0].lower() == "select" : 
            self.select(line)     
        if line[0].lower() == "project": 
            self.project(line)       
        if line[0].lower() == "rename" : 
            self.rename(line)      
        if line[1] == "<-"             : 
            self.relational(line)
    
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
    lexicon = Lexer(os.path.join(__location__, 'test.txt'))
    
Main() # Needed to make Main work.     
    
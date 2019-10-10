# CSCE_315_2019
Python implementation of IMDB from scratch.

## Just to make a scenario:
>tablename := "Ships"\
>row_attribute_name_string := "Age"\
>row_key := "1234"\
>Table := self.tables[tablename]\
>Row := self.tables[tablename][row_key]\
>Row attribute := self.tables[tablename][row_key][attribute_name_string]

## From here, checking the schema
>List of ordered variable names := self.schemas[tablename]["attributes"]\
>List of variable types := self.schemas[tablename]["types"]\
>List of (variable, type) pairs for a table := zip(self.schemas[tablename]["attributes"], self.schemas[tablename]["types"])

## Rows (since you won't have the keys yourself) are iterable with:
>for x in self.tables[tablename].keys():\
>and you access each row with self.tables[tablename][x]

## In order to test the code
Simply run "python regex_lexicon.py" with both that file, and test.txt in the same directory as the command prompt.

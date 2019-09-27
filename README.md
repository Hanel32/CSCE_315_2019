# CSCE_315_2019
Python implementation of IMDB from scratch.\

##Just to make a scenario:\
tablename := "Ships"\
Table := self.tables[tablename]\
Row := self.tables[tablename][row_key]\
Row attribute := self.tables[tablename][row_key][attribute_name_string]\

##From here, checking the schema\
List of ordered variable names := self.schemas[tablename]["attributes"]\
List of variable types := self.schemas[tablename]["types"]\
List of (variable, type) pairs for a table := zip(self.schemas[tablename]["attributes"], self.schemas[tablename]["types"])\

##Rows (since you won't have the keys yourself) are iterable with:\
for x in self.tables[tablename].keys():\
and you access each row with self.tables[tablename][x]\

import regex_lexicon as engine
import json
import os

class DB(object):
    def run_cmd(self, line):
        return self.engine.run_cmd(line)
    
    def fetch_json(self, loc):
        __location__  = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
        datapath      = os.path.join(__location__, loc)
        data          = open(datapath, "r", encoding = 'utf-8')
        return json.load(data)
    
    def build_dictionary(self, json):
        dictionary = {}
        for obj in json:
            for attribute, value in obj.items():
                if attribute == "id":
                    dictionary[int(value)] = obj
        return dictionary
    
    def parse_schema(self, record):
        schema    = []
        variables = []
        for variable_name in record.keys():
            if isinstance(record[variable_name], (list, dict)):
                schema.append("LIST")
                variables.append(variable_name)
            elif str(record[variable_name]).isdigit():
                schema.append("INTEGER")
                variables.append(variable_name)
            else:
                schema.append("VARCHAR(40)")
                variables.append(variable_name)
        return (schema, variables)
    
    def build_list_tables(table, variable):
        # Create the unique ID dictionary
        id_dict = {}
        for x in table.keys():
            for y in table[x][variable]:
                if y['id'] not in id_dict.keys():
                    id_dict[y['id']] = y['name']
                    
        # Turn the list of dictionaries into ids
        for x in table.keys():
            for y in table[x][variable]:
                y = y['id']
                
        # Return the dictionary of ids
        return id_dict
    
    def __init__(self):
        # Create a database object
        self.engine   = engine.Lexer()
        
        # Parse through the movies, and turn the list into a dictionary
        movies        = self.build_dictionary(self.fetch_json('movie_data/movies.json'))
        
        # Parse through the cast, and turn the list into, again, a dictionary'
        cast          = self.build_dictionary(self.fetch_json('movie_data/credits.json'))
        
        # Extract schema name and variables from movies
        packed_schema = self.parse_schema(movies[891])
        movie_schema  = packed_schema[0]
        movie_vars    = packed_schema[1]
        
        # Extract schema name and variables from cast
        packed_schema = self.parse_schema(cast[891])
        cast_schema   = packed_schema[0]
        cast_vars     = packed_schema[1]
        
        # Create ACTORS/MOVIES/CHARACTERS tables
        actor = "CREATE TABLE actors (id INTEGER, name VARCHAR(40), movies VARCHAR(1024), \
                  characters VARCHAR(1024), best_movie INTEGER) PRIMARY KEY (id);"
        movie = "CREATE TABLE movies (id INTEGER, title VARCHAR(40), actors VARCHAR(1024), \
                  genres VARCHAR(1024), directors_worst INTEGER) PRIMARY KEY (id);"
        chars = "CREATE TABLE characters (name VARCHAR(40), actors_played VARCHAR(1024), \
                  PRIMARY KEY (name);"
        self.engine.run_cmd(actor)
        self.engine.run_cmd(movie)
        self.engine.run_cmd(chars)
            
        # Build all records for ACTORS
        actors = {}
        for x in cast.keys():
            for y in cast[x]['cast']:
                if y['id'] not in actors.keys():
                    actors[y['id']]   = {}
                    rec               = actors[y['id']]
                    rec['name']       = y['name']
                    rec['movies']     = []
                    rec['movies'].append(cast[x]['id'])
                    rec['characters'] = []
                    rec['characters'].append(y['character'])
                    rec['best_movie'] = cast[x]['id']
                    rec['best_rate']  = int(float(movies[x]['vote_average']) * 10)
                else:
                    rec               = actors[y['id']]
                    rec['movies'].append(cast[x]['id'])
                    rec['characters'].append(y['character'])
                    if int(float(movies[x]['vote_average']) * 10) > rec['best_rate']:
                        rec['best_rate']  = int(float(movies[x]['vote_average']) * 10)
                        rec['best_movie'] = cast[x]['id']
        # Remove duplicates.
        for x in actors.keys():
            actors[x]['movies']     = set(actors[x]['movies'])
            actors[x]['characters'] = set(actors[x]['characters'])
            
        # Build all records for MOVIES
        movie  = {}
        for x in movies.keys():
            movie[x]      = {}
            rec           = movie[x]
            rec['title']  = movies[x]['original_title']
            rec['actors'] = []
            rec['genres'] = []
            for y in cast[x]['cast']:
                rec['actors'].append(y['id'])
            for y in movies[x]['genres']:
                rec['genres'].append(y['name'])
                
        print(movies[891]['genres'])
        # Build all records for CHARACTERS
            
        #print(actors[1])
                
        
        movies     = {}
        characters = {}
        
        # Insert the built records into the DBMS
        
        print("\nMOVIES")
        for x in zip(movie_schema, movie_vars):
            print(x)
            
        print("\nCAST")
        for x in zip(cast_schema, cast_vars):
            print(x)
        
        
        
        # Make insertable records of data
        #db      = movies
        #inserts = []
        #for row in db.keys():
        #    values = []
        #    for variable in db[row].keys():
        #        values.append(str(movies[row][variable]))
        #    inserts.append("INSERT INTO movies VALUES FROM (" + ", ".join(values) + ");")
            
        
DB()
        
        
        
        
        
        
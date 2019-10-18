import regex_lexicon as engine
import json
import os

class DB(object):
    # Assures data is in the correct format.
    def format_array(self, data):
        return "\"" + "|".join(data).replace("\"", "").replace(",", "").replace(" ", "_") + "\""
    
    # Forwards a command to the data model.
    def run_cmd(self, line):
        return self.engine.run_cmd(line)
    
    # Grabs the JSON files from disk.
    def fetch_json(self, loc):
        __location__  = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
        datapath      = os.path.join(__location__, loc)
        data          = open(datapath, "r", encoding = 'utf-8')
        return json.load(data)
    
    # Builds a dictionary from json
    def build_dictionary(self, json):
        dictionary = {}
        for obj in json:
            for attribute, value in obj.items():
                if attribute == "id":
                    dictionary[int(value)] = obj
        return dictionary
    
    # Parses a schema from a given dictionary record. Depricated.
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
    
    # Create the unique ID dictionary
    def build_list_tables(table, variable):
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
    
    def sql_injection(self, table, variables, db_tablename):
        # Make insertable records of data
        inserts = []
        for row in table.keys():
            values = []
            if not isinstance(row, int) and not row.isdigit():
                values.append("\"" + row.replace(" ", "_") + "\"")
            else:
                values.append(row)
            if len(variables) > 2:
                for variable in variables[1:]:
                    values.append(str(table[row][variable]))
            else:
                values.append(str(table[row]))
            values = map(str, values)
            inserts.append("INSERT INTO " + str(db_tablename) + " VALUES FROM (" + str(", ".join(values)) + ");")
        for cmd in inserts:
            self.run_cmd(cmd)
    
    def __init__(self):
        # Create a database object
        self.engine   = engine.Lexer()
        
        # Check if file exists
        __location__  = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
        datapath      = os.path.join(__location__, "movies.csv")
        
        # If the DB has been parsed, load it from csv.
        if(os.path.exists(datapath)):
            self.run_cmd("OPEN movies;")
            self.run_cmd("OPEN actors;")
            self.run_cmd("OPEN characters;")
        
        # Otherwise, first time, parse the JSON.
        else:
            # Parse through the movies, and turn the list into a dictionary
            movies        = self.build_dictionary(self.fetch_json('movie_data\movies.json'))
            
            # Parse through the cast, and turn the list into, again, a dictionary'
            cast          = self.build_dictionary(self.fetch_json('movie_data\credits.json'))
            
            # Create ACTORS/MOVIES/CHARACTERS tables commands
            actor = "CREATE TABLE actors (id INTEGER, name VARCHAR(80), movies VARCHAR(10000), characters VARCHAR(10000), best_movie INTEGER) PRIMARY KEY (id);"
            movie = "CREATE TABLE movies (id INTEGER, title VARCHAR(800), actors VARCHAR(10000), genres VARCHAR(10000), directors_worst INTEGER) PRIMARY KEY (id);"
            chars = "CREATE TABLE characters (name VARCHAR(8000), actors_played VARCHAR(100000), id INTEGER) PRIMARY KEY (id);"
                      
            # Run the commands on the DB.
            self.engine.run_cmd(actor)
            self.engine.run_cmd(movie)
            self.engine.run_cmd(chars)
                
            # Build all records for ACTORS and CHARACTERS
            actors     = {}
            characters = {}
            for x in cast.keys():
                for y in cast[x]['cast']:
                    # ACTORS building
                    if y['id'] not in actors.keys():
                        actors[y['id']]   = {}
                        rec               = actors[y['id']]
                        rec['name']       = "\"" + y['name'].replace(" ", "_") + "\""
                        rec['movies']     = []
                        rec['movies'].append(cast[x]['id'])
                        rec['best_movie'] = cast[x]['id']
                        rec['best_rate']  = int(float(movies[x]['vote_average']) * 10)
                        rec['characters'] = []
                        rec['characters'].append("\"" + y['character'] + "\"")
                    else:
                        rec               = actors[y['id']]
                        rec['movies'].append(cast[x]['id'])
                        rec['characters'].append(y['character'])
                        if int(float(movies[x]['vote_average']) * 10) > rec['best_rate']:
                            rec['best_rate']  = int(float(movies[x]['vote_average']) * 10)
                            rec['best_movie'] = cast[x]['id']    
                    # CHARACTERS building
                    if y['character'] not in characters.keys():
                        key             = y['character']
                        characters[key] = {}
                        characters[key]['actors_played'] = []
                        characters[key]['actors_played'].append(y['name'])
                    else:
                        key             = y['character']
                        characters[key]['actors_played'].append(y['name'])
                        
            # Remove duplicates, turn lists to strings.
            for x in actors.keys():
                actors[x]['movies']     = set(actors[x]['movies'])
                actors[x]['characters'] = set(actors[x]['characters'])
                actors[x]['movies']     = self.format_array(actors[x]['movies'])
                actors[x]['characters'] = self.format_array(actors[x]['characters'])
            i = 0
            for x in characters.keys():
                characters[x]['actors_played'] = set(characters[x]['actors_played'] )
                characters[x]['actors_played'] = self.format_array(characters[x]['actors_played'])
                characters[x]['id'] = i
                i += 1
                
            # Build all records for MOVIES
            movie           = {}
            directors_worst = {}
            for x in movies.keys():
                movie[x]      = {}
                rec           = movie[x]
                rec['title']  = "\"" + movies[x]['original_title'].replace(" ", "_") + "\""
                rec['actors'] = []
                rec['genres'] = []
                for y in cast[x]['cast']:
                    rec['actors'].append(y['id'])
                for y in movies[x]['genres']:
                    rec['genres'].append(y['name'])
                rec['actors'] = map(str, rec['actors'])
                rec['actors'] = self.format_array(rec['actors'])
                rec['genres'] = self.format_array(rec['genres'])
                rec['directors_worst'] = 0
                
                # Find the director
                for person in cast[x]['crew']:
                    if 'director' in person['job'].lower():
                        d_id = person['id']
                        if d_id not in directors_worst.keys():
                            directors_worst[d_id] = []
                            directors_worst[d_id].append(x)
                            break
                        else:
                            directors_worst[d_id].append(x)
                            break
                
            # Calculate each director's worst movie.
            for x in directors_worst.keys():
                key   = directors_worst[x][0]
                worst = key
                score = int(movies[key]['vote_average'] * 10)
                
                # Iterate through directed movies; find worst.
                for mov in directors_worst[x][1:]:
                    new_score = int(movies[mov]['vote_average'] * 10)
                    if new_score < score:
                        score = new_score
                        worst = mov
                # Save the worst
                for mov in directors_worst[x]:
                    movie[mov]['directors_worst'] = worst
                    
            # Save the order of entry of the variables in a list; hash loses order.
            actor_vars = ['id', 'name', 'movies', 'characters', 'best_movie']
            movie_vars = ['id', 'title', 'actors', 'genres', 'directors_worst']
            chars_vars = ['name', 'actors_played', 'id']
        
            # Inject all of the data into the database.
            self.sql_injection(actors,     actor_vars, 'actors')
            self.sql_injection(movie,      movie_vars, 'movies')
            self.sql_injection(characters, chars_vars, 'characters') 
            
            # Write the data to disk
            self.run_cmd("WRITE movies;")
            self.run_cmd("WRITE actors;")
            self.run_cmd("WRITE characters;")
        
        
        
        
        
        
        
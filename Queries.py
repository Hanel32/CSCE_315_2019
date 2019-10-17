import regex_lexicon
import JSON_Parser
import random
import string

class Queries:

    class StepToActorB :
        def __init__(self, number, name, movie):
            self.number = number
            self.name = name
            self.movie = movie

    def randomString(self, stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def StringToList(self, string) :
        listFromString = string.split('|')
        return listFromString

    # Actually performs the Bacon Number calculation
    def BaconNumberRecursive(self, actorB, actorsTable, moviesTable, actorsList, baconNumber) :

        baconNumber += 1
        print("bacon number: " + str(baconNumber))

        # Make empty list of some data structure that holds the bacon number, an actor name, and a movie
        pathToActorB = []
        # Make empty list of actor IDs
        actorIDs = []

        for sourceActor in actorsList :
            movieList = self.StringToList(actorsTable[sourceActor]['movies'])
            for movie in movieList :
                actorList = self.StringToList(moviesTable[movie]['actors'])
                for actor in actorList :
                    actorName = actorsTable[actor]['name'].replace(" ", "_")
                    #print(actorName)
                    # add actor's ID to list (skip duplicates)
                    if not actor in actorIDs :
                        actorIDs.append(actor)
                    if actorName == actorB :
                        # add Bacon Number, actor's name, movie to the list at start
                        newStep = self.StepToActorB(baconNumber, actorsTable[sourceActor]['name'].replace(" ", "_"), moviesTable[movie]['title'])
                        pathToActorB.append(newStep)
                        return pathToActorB

        # newMovieList = []
        # for actorId in actorIDs :
        #     newMovieList += self.StringToList(actorsTable[actorId]['movies'])

        # # removes duplicate movies
        # newMovieList = list(dict.fromkeys(newMovieList))

        pathToActorB += self.BaconNumberRecursive(actorB, actorsTable, moviesTable, actorIDs, baconNumber)
        return pathToActorB

    # Calls the actual worker function, and interprets the output into a string
    def BaconNumber(self, actorAOrig, actorBOrig) : # These are the actor's names as strings

        print("Bacon Number called")

        actorA = actorAOrig.replace(" ", "_")
        actorB = actorBOrig.replace(" ", "_")

        if actorA == "" or actorB == "" :
            return ""

        # Get reference to the different tables I need
        newTblName = self.randomString()
        actorsTable = self.DB.run_cmd(newTblName + " <- project (id, name, movies) actors;")

        newTblName1 = self.randomString()
        moviesTable = self.DB.run_cmd(newTblName1 + " <- project (id, title, actors) movies;")

        # Get actorA's movie list
        newTblName = self.randomString()
        actorAData = self.DB.run_cmd(newTblName + " <- select (name == \"" + actorA + "\") actors;")
        actorAID = " "
        for key in actorAData :
            movieListA = self.StringToList(actorAData[key]['movies'])
            actorAID = key

        actorList = []
        actorList.append(actorAID)

        baconPath = self.BaconNumberRecursive(actorB, actorsTable, moviesTable, actorList, 0)

        retString = "Bacon Number: " + str(baconPath[-1].number) + '\n' + "Path: " + actorAOrig + " -> "

        # index = 0
        # while index < len(baconPath) - 1 :
        for item in baconPath :
            retString += item.movie.replace("_", " ") + " -> " + item.name.replace("_", " ")
            # index += 1

        return retString

    def Typecasting(self, actorToUse) :

        actor = actorToUse.replace(" ", "_")

        if actor == "" :
            return ""

        # Make an object that holds a genre and an int representing number of movies in said genre for the actor
        class GenreAndCount :
            def __init__(self, genreName, genreCount):
                self.genreName = genreName
                self.genreCount = genreCount

        # Make an empty list of these objects
        genreCounts = []

        # Get actor's data from DB
        newTblName = self.randomString()
        actorData = self.DB.run_cmd(newTblName + " <- select (name == \"" + actor + "\") actors;")
        actorID = " "
        for key in actorData :
            actorID = key

        # Get list of movies for this actor
        movieList = self.StringToList(actorData[actorID]['movies'])

        # Get the movies table for easy access
        newTblName1 = self.randomString()
        moviesTable = self.DB.run_cmd(newTblName1 + " <- project (id, genres) movies;")

        # Iterate through all the movies (by ID) the actor has starred in
        for movie in movieList :
            genreList = self.StringToList(moviesTable[movie]['genres'])
            # Used to make new genre objects when appropriate
            genresToCheck = genreList
            # Iterate through all the genres from an actor's movies
            for genre in genreCounts :
                # Check the current genre against all the genres for this movie
                for movieGenre in genreList :
                    if movieGenre.lower() == genre.genreName.lower() :
                        genre.genreCount += 1
                        # Get rid of this element, as we have already checked it
                        genresToCheck.remove(movieGenre)

            # Will only operate on any genres that movie had that weren't already in the list
            for genre in genresToCheck :
                newGenre = GenreAndCount(genre, 1)
                genreCounts.append(newGenre)

        # Find the genre with the highest amount
        maxCountOfGenre = 0
        maxGenre = genreCounts[0]

        for item in genreCounts:
            if item.genreCount > maxCountOfGenre:
                maxCountOfGenre = item.genreCount
                maxGenre = item

        retString = str(actorToUse) + " has starred in more " + str(maxGenre.genreName) + " movies than"
        retString += " any other genre, having appeared in " + str(maxGenre.genreCount) + " movies of this genre."

        return retString
    
    def CoverRoles(self, characterName):
        characterData = self.DB.run_cmd("temp <- select (name == " + characterName + ") characters;")
        for char in characterData:
            charData = characterData[char]
            name = char
        self.DB.run_cmd("DELETE FROM temp WHERE id == " + name + ";")

        CoverRoleActors = charData["actors_played"]

        retString = "The following actors have played " + characterName + " :\n"

        # Adds all actor names to retString
        for actor in CoverRoleActors:
            retString = retString + actor + ", "

        # Remove last comma if one was added
        if len(CoverRoleActors) != 0:
            retString = retString[:-2]

        #print(retString)

        return retString

    def BestWorstDays(self, actorName) :
        # Get actor's data from DB
        actorData = self.DB.run_cmd("temp <- select (name == " + actorName + ") actors;")
        self.DB.run_cmd("DELETE temp;")

        # Obtains the actor's best ranked movie
        bestMovie = actorData["best_movie"]

        # Obtains the data for that movie
        movieData = self.DB.run_cmd("temp <- select (id == " + bestMovie + ") movies;")
        self.DB.run_cmd("DELETE temp;")

        # Obtains the worst ranked movie of the same director as that movie
        worstMovie = movieData["directors_worst"]

        # Creates retString to display results to user
        retString = "The highest rated movie " + actorName + " has appeared in is " + bestMovie + ".\n" \
                  + "The lowest rated movie directed by " + bestMovie["name"] + "'s director is " + worstMovie

        #print(retString)

        return retString

        return worstMovie

    def constellation(self, actor, num=1):
        costar_constellation = {}
        num = int(num)
        actor = actor.replace(" ", "_")

        # Get actor info and movie list
        actor_info = self.DB.run_cmd("temp <- select (name == " + actor + ") actors;")
        for a in actor_info:
            movies = self.StringToList(actor_info[a]["movies"])
        self.DB.run_cmd("DELETE temp;")

        # Get actor (id, name, movies) table
        costar_info = self.DB.run_cmd("temp <- project (id, name, movies) actors;")

        # Fill costar_constellation dict with costar_constellation[costar] = numMoviesTogether
        for costar in costar_info:
        	costar = costar_info[costar]
        	costar_constellation[costar["name"]] = 0

            # Check for each movie and increment entry if a match
        	for movie in movies:
        		if movie in costar["movies"]:
        			costar_constellation[costar["name"]] = costar_constellation[costar["name"]] + 1

        # Search through costar table and select those with num appearances
        matches = []
        for costar, appearances in costar_constellation.items():
        	if (appearances == num) & (costar != actor):
        		matches.append(costar)

        # Delete temp
        self.DB.run_cmd("DELETE temp;")

        # Find actor list for each movie and add to list
        for movie in movies:
            # Get actor list
            movie = self.DB.run_cmd("temp <- select (id == " + movie + ") movies;")
            for m in movie:
                actors = self.StringToList(movie[m]["actors"])
                name = m
            self.DB.run_cmd("DELETE FROM temp WHERE id == " + name + ";")

            # Add each actor to costar dictionary and update number of appearances
            for a in actors:
                # Only add if a is not input actor
                if a != actor:
                    # If actor is already in list, increment appearances
                    if a in costar_list:
                        costar_list[a] = costar_list[a] + 1
                    # Add actor to list
                    else:
                        costar_list[a] = 1

        # Look through costar_list and return costars with num of appearances
        costar_constellation = []
        for costar,appearances in costar_list.items():
            if appearances == num:
                costar_constellation.append(costar)

        # Get names from ID numbers
        for i in range(len(costar_constellation)):
            star = self.DB.run_cmd("temp <- select (id == " + costar_constellation[i] + ") actors;")
            for s in star:
                costar_constellation[i] = star[s]["name"]
                name = s
            self.DB.run_cmd("DELETE FROM temp WHERE id == " + name + ";")

        #print(costar_constellation)

        return costar_constellation

    def __init__(self) :
        self.DB = JSON_Parser.DB()
        self.engine = regex_lexicon.Lexer()


def Main() :
    queries = Queries()
    # print(queries.BaconNumber("Uwe Boll", "Christopher Lee"))
    # print(queries.BaconNumber("Kevin Bacon", "John Cena"))
    # print("Bacon Number done")
    print(queries.Typecasting("Christopher Lee"))

Main()
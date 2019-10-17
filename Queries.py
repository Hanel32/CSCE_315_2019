import regex_lexicon
import JSON_Parser

class Queries:

    def StringToList(self, string) :
        listFromString = string.split(', ')
        return listFromString

    def BaconNumber(self, actorAOrig, actorBOrig) : # These are the actor's names as strings

        actorA = actorAOrig.lower()
        actorB = actorBOrig.lower()

        if actorA == "" or actorB == "" :
            return ""

        class StepToActorB :
            def __init__(self, number, name, movie):
                self.number = number
                self.name = name
                self.movie = movie

        # Initialize Bacon Number at 1
        baconNumber = 1

        # Make empty list of some data structure that holds the bacon number, an actor name, and a movie
        pathToActorB = []

        # Get actorA's data from the DB
        actorAData = self.DB.run_cmd("temp <- select (name == " + actorA + ") actors;")
        movieListA = self.StringToList(actorAData["movies"])
        DB.run_cmd("DELETE temp;")

        # Make empty list of actor IDs
        actorIDs = []

        for movie in movieListA :

            movieData = self.DB.run_cmd("temp <- select (id == " + movie + ") movies;")
            actorList = self.StringToList(movieData["actors"])
            DB.run_cmd("DELETE temp;")

            for actor in actorList :

                actorData = self.DB.run_cmd("temp <- select (id == " + actor + ") actors;")
                actorName = actorData["name"].lower()
                DB.run_cmd("DELETE temp;")

                # add actor's ID to list (skip duplicates)
                if not actor in actorIDs :
                    actorIDs.append(actor)
                if actorName == actorB :
                    # add Bacon Number, actor's name, movie to the list at start
                    newStep = StepToActorB(baconNumber, actorName, movie)
                    pathToActorB.append(newStep)
                    return pathToActorB
    
        baconNumber += 1

        # Make empty list of returns from the following for loop
        baconReturns = []
        
        for actor in actorIDs :
            otherActorData = self.DB.run_cmd("temp <- select (id == " + actor + ") actors;")
            otherActorName = otherActorData["name"].lower()
            DB.run_cmd("DELETE temp;")

            # add BaconNumber(actor name, actorB) to list
            baconReturns.append(self.BaconNumber(actorAOrig, otherActorName))

        lowestNumber = baconReturns[0][-1].number
        listToAdd = baconReturns[0]

        # Combine the list with the lowest highest Bacon number from above to the list at the start
        for item in baconReturns :
            if item[-1].number < lowestNumber :
                lowestNumber = item[-1].number
                listToAdd = item
        
        pathToActorB = pathToActorB + listToAdd

        returnString = "Bacon Number: " + pathToActorB[-1].number + '\n' + "Path:\n" + actorAOrig + '\n'

        for item in pathToActorB :
            returnString = returnString + item.movie + '\n' + item.name + '\n'

        print(returnString)

        # return this list/display it to GUI
        return returnString

    def Typecasting(self, actorToUse) :

        actor = actorToUse.lower()

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
        actorData = self.DB.run_cmd("temp <- select (name == " + actor + ") actors;")

        movieList = self.StringToList(actorData["movies"])

        DB.run_cmd("DELETE temp;")

        # Iterate through all the movies (by ID) the actor has stared in
        for movie in movieList :

            # Get the movie's data from DB
            movieData = self.DB.run_cmd("temp <- select (id == " + movie + ") movies;")

            genreList = self.StringToList(movieData["genres"])

            DB.run_cmd("DELETE temp;")

            # Used to make new genre objects when appropriate
            genresToCheck = genreList

            # Iterate through all the genres from an actor's movies
            for genre in genreCounts :
                # Check the current genre against all the genres for this movie
                for movieGenre in genreList :
                    if movieGenre == genre :
                        genre.genreCount += 1
                        # Get rid of this element, as we have already checked it
                        genresToCheck.remove(movieGenre)

            # Will only operate on any genres tha movie had that weren't already in the list
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

        retString = actorToUse + " has starred in more " + maxGenre.genreName + " movies than \
            any other genre, having appeared in " + maxGenre.genreCount + " of these movies."

        print(retString)

        return retString
    
    def CoverRoles(self, characterName):
        characterData = self.DB.run_cmd("temp <- select (characters == " + characterName + ") characters;")
        self.DB.run_cmd("DELETE temp;")

        CoverRoleActors = characterData["actors_played"];

        retString = "The following actors have played " + characterName + " :\n"

        # Adds all actor names to retString
        for actor in CoverRoleActors:
            retString = retString + actor + ", "

        # Remove last comma if one was added
        if len(CoverRoleActors) != 0:
            retString = retString[:-2]

        print(retString)

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

        print(retString)

        return retString

        return worstMovie

    def constellation(self, actor, num):
        costar_list = {}
        num = int(num)

        # Get actor info and movie list
        actor = self.DB.run_cmd("hey <- select (name == " + actor + ") actors;")
        movies = self.StringToList(actor["movies"])
        DB.run_cmd("DELETE hey;")

        # Find actor list for each movie and add to list
        for movie in movies:
            # Get actor list
            movie = self.DB.run_cmd("tmp <- select (title == " + movie + ") movies;")
            actors = self.StringToList(movie["actors"])
            DB.run_cmd("DELETE tmp;")

            # Add each actor to costar dictionary and update number of appearances
            for a in actors:
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

        return costar_constellation

    def __init__(self) :
        self.DB = JSON_Parser.DB()
        self.engine = regex_lexicon.Lexer()


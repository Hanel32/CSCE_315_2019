import regex_lexicon as engine
import JSON_Parser as DB

class Queries:

    def BaconNumber(self, actorA, actorB) : # These are the actor's names as strings

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

        # Make empty list of actor ID's
        actorIDs = []

        # for movie in actorA's movies :
            # for actor in movie :
                # add actor's ID to list (skip duplicates)
                # if not actor in actorIDs :
                    # actorIDs.append(actor)
                # if actor's name == actorB :
                    # add Bacon Number, actor's name, movie to the list at start
                    # return said list
        
        # Bacon Number++
        # Make empty list of returns from the following for loop
        
        # for actor ID in list :
            # add BaconNumber(actor name, actorB) to list

        # Combine the list with the lowest highest Bacon number from above to the list at the start

        # return this list/display it to GUI

    def Typecasting(self, actor) :

        # Make an object that holds a genre and an int representing number of movies in said genre for the actor
        class GenreAndCount :
            def __init__(self, genreName, genreCount):
                self.genreName = genreName
                self.genreCount = genreCount

            def toString() :
                return genreName + " " + str(genreCount)

        # Make an empty list of these objects
        genreCounts = []

        # Get actor's data from DB
        actorData = DB.run_cmd("temp <- select (name == " + actor + ") actors")
        DB.run_cmd("DELETE temp")

        # Iterate through all the movies (by ID) the actor has stared in
        for movie in actorData["movies"] :

            # Get the movie's data from DB
            movieData = DB.run_cmd("temp <- select (id == " + movie + ") movies")
            DB.run_cmd("DELETE temp")

            # Used to make new genre objects when appropriate
            genresToCheck = movieData[genres]

            # Iterate through all the genres from an actor's movies
            for genre in genreCounts :
                # Check the current genre against all the genres for this movie
                for movieGenre in movieData[genres] :
                    if genre == movieGenre :
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

        retString = actor + " has starred in more " + maxGenre.genreName + " movies than \
            any other genre, having appeared in " + maxGenre.genreCount + " of these movies"

        print(retString)

        return retString

        # return maxGenre/output results to GUI
   
    def BestWorstDays(self, actorName) :
        # Get actor's data from DB
        actorData = DB.run_cmd("temp <- select (name == " + actorName + ") actors;")
        DB.run_cmd("DELETE temp;")

        # Obtains the actor's best ranked movie
        bestMovie = actorData["best_movie"]

        # Obtains the data for that movie
        movieData = DB.run_cmd("temp <- select (id == " + bestMovie + ") movies;")
        DB.run_cmd("DELETE temp;")

        # Obtains the worst ranked movie of the same director as that movie
        worstMovie = movieData["directors_worst"]

        return worstMovie
    
    def __init__(self) :
        self.DB = JSON_Parser.DB()
        self.engine = regex_lexicon.Lexer()

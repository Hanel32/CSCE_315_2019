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

        # Make an empty list of these objects
        genreCounts = []

        # Get actor's data from DB

        # for movie in actor's movies :

            genreExistsInList = False

            for genre in genreCounts :
                # if movie's genre == object's genre :
                    genre.genreCount += 1
                    genreExistsInList = True
                    break

            if not genreExistsInList :
                # newGenre = GenreAndCount(movie's genre, 1)
                # genreCounts.append(newGenre)

        maxCountOfGenre = 0
        maxGenre = genreCounts[0]

        for item in genreCounts:
            if item.genreCount > maxCountOfGenre:
                maxCountOfGenre = item.genreCount
                maxGenre = item

        # return maxGenre/output results to GUI

        


# You are tasked with developing a movie recommendation system. You are given a list of
# movies (their names) and a list of similarities between movies (pairs of movies that
# are similar). You are also given a list of user's friends and for each friend a list
# of movies that he has already seen.
#
# Your system should recommend one movie with the highest discussability and uniqueness.
# Discussability is the number of friends of user, who have already seen that movie.
# Uniqueness is 1 divided by the mean number of similar movies that the user's friends
# have already seen. So you should return the film with the highest number: F / S,
# where F = number of friends who have seen this movie, and S = mean of the number of
# similar movies seen for each friend.

import csv
import ast
import itertools
import random


# Rad films from csv file (f_name)
def get_films(f_name):
    data = {}
    data_header = ['star_rating', 'title', 'content_rating', 'genre', 'duration', 'actors_list']

    with open(f_name, newline='') as f:
        reader = csv.reader(f)
        film_index = -1

        for row in reader:
            # Skip header in CSV file
            if film_index == -1:
                film_index += 1
                continue

            data[film_index] = dict(zip(data_header, row))
            film_index += 1

    return data


# Find similarity between films by actors, who played in more than only one movie.
# As result, function return list of tuples with similar film ID's,
# for example: [(123, 456), (456, 789)]. Result contains all combinations of similar
# films without permutations (as can see in example). Similarities are possesses
# the transitive property, it mean's '123' and '789' are similarity too
def get_similarity(films_list):
    actors = {}

    for id, desc in films_list.items():
        actors_list = ast.literal_eval(desc['actors_list'])
        for actor in actors_list:
            if actor in actors:
                actors[actor].append(id)
            else:
                actors[actor] = []

    # Get actors, who played in more than only one movie
    actors_top = {actor: films_id for (actor, films_id) in actors.items() if len(films_id) > 1}

    similarity_list = []

    for films_id in actors_top:
        for pair in itertools.combinations(actors_top[films_id], 2):
            if pair not in similarity_list:
                similarity_list.append(pair)

    return similarity_list


# Generate dict of users with random films
def get_user_friends(films):
    friends = {}
    friends_cnt = random.randint(10, 50)

    for friend_id in range(friends_cnt):
        films_cnt = random.randint(5, 100)

        for _ in range(films_cnt):
            if friend_id in friends:
                friends[friend_id].append(random.choice(list(films.keys())))
            else:
                friends[friend_id] = []

    return friends


def get_films_discussability(user_friends):
    discussability = {}

    for _, films in user_friends.items():
        for film_id in films:
            if film_id in discussability:
                discussability[film_id] += 1
            else:
                discussability[film_id] = 1

    # Check discussability's correct calculation
    # print({k: v for k, v in sorted(discussability.items(), key=lambda item: item[1], reverse=True)})

    return discussability


def convert_to_adj_dict(lst):
    adj_dict = {}

    for (v1, v2) in lst:
        if v1 in adj_dict:
            if v2 not in adj_dict[v1]:
                adj_dict[v1].append(v2)
        else:
            adj_dict[v1] = [v2]

        if v2 in adj_dict:
            if v1 not in adj_dict[v2]:
                adj_dict[v2].append(v1)
        else:
            adj_dict[v2] = [v1]

    return adj_dict


def get_component_for_films(similarity_list):
    adj_dict = convert_to_adj_dict(similarity_list)
    film_component = {}
    num_components = 0

    visited = {}

    def dfs(v):
        film_component[v] = num_components
        visited[v] = True
        for w in adj_dict[v]:
            if w not in visited:
                dfs(w)

    for v in adj_dict:
        if v not in visited:
            dfs(v)
            num_components += 1

    return film_component


# Uniqueness is mean number of similar movies that the user's friends have already seen
def get_films_uniqueness(discussability, similarity_list, user_friends):
    uniqueness = {}
    components = get_component_for_films(similarity_list)

    for film_id in discussability:
        total_similar_films = 0

        for _, friends_film_list in user_friends.items():
            for friend_film_id in friends_film_list:
                if film_id not in components or friend_film_id not in components:
                    continue
                if components[film_id] == components[friend_film_id]:
                    total_similar_films += 1

        mean_value = total_similar_films / len(user_friends)
        uniqueness[film_id] = mean_value

    return uniqueness


# Main function for recommend one movie with the highest discussability
# and uniqueness
def film_recommend(similarity_list, user_friends):
    discussability = get_films_discussability(user_friends)
    uniqueness = get_films_uniqueness(discussability, similarity_list, user_friends)

    # Return the film with the highest number: F / S, where F = number
    # of friends who have seen this movie, and S = mean of the number
    # of similar movies seen for each friend.

    highest_value = 0
    highest_films = []

    for film_id in discussability.keys():
        if film_id in uniqueness:
            if film_id not in uniqueness or uniqueness[film_id] == 0:
                value = 0
            else:
                value = discussability[film_id] / uniqueness[film_id]

            if value > highest_value:
                highest_value = value
                highest_films = [film_id]

            elif value == highest_value:
                highest_films.append(film_id)
        else:
            continue

    return (highest_films, highest_value)


films_list = get_films('imdb_1000.csv')
print(f'Films: {films_list}\nCount of films: {len(films_list)}\n')

similarity_list = get_similarity(films_list)
print(f'Similarity list: {similarity_list}\nCount of sim. list: {len(similarity_list)}\n')

user_friends = get_user_friends(films_list)
print(f'Friends: {user_friends}\nCount of friends: {len(user_friends)}\n')


best_films_id, best_films_rate = film_recommend(similarity_list, user_friends)

for film_id in best_films_id:
    print(f'Recommend film: ID = {film_id}, Title = {films_list[film_id]["title"]}, Rate = {best_films_rate}')

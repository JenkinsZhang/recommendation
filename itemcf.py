import numpy as np
import math
import time
import random
from collections import defaultdict
from operator import itemgetter
movieset={}
trainset={}
testset={}
n_sim_movie=30
n_rec_movie=10
movie_sim_mat={}
movie_popular={}
movie_count=0

def generate_moviedata(filename):
    print('loading movies.dat')
    f=open(filename)
    for line in f.readlines():
        line=line.strip('\r\n')
        movieid,moviename,moviecat=line.split('::')
        movieset[movieid]=moviename
    print('load movies.dat succ')

def loadfile(filename):
    f=open(filename,'r')
    for line in f:
        yield line.strip('\r\t')
    f.close()
    print('load %s succ' % filename)

def generate_dataset(filename, pivot=0.8):
    print('start spliting dataset')
    trainset_len = 0
    testset_len = 0

    for line in loadfile(filename):
        user, movie, rating, _ = line.split('::')
        if random.random() < pivot:
            trainset.setdefault(user, {})
            trainset[user][movie] = int(rating)
            trainset_len += 1
        else:
            testset.setdefault(user, {})
            testset[user][movie] = int(rating)
            testset_len += 1

    print ('split training set and test set succ')
    print ('train set length = %s' % trainset_len)
    print ('test set length = %s' % testset_len)

def calc_movie_sim():
    global movie_count
    print('counting movies numbers and popularity...')

    for user, movies in trainset.items():
        for movie in movies:
            if movie not in movie_popular:
                movie_popular[movie] = 0
            movie_popular[movie] += 1

    print('count movies numbers and popularity succ')

    movie_count = len(movie_popular)
    print('total movie number = %d' % movie_count)

    itemsim_mat = movie_sim_mat
    print('generating item co-rated matrix...')
    for user, movies in trainset.items():
        for m1 in movies:
            itemsim_mat.setdefault(m1, defaultdict(int))
            for m2 in movies:
                if m1 == m2:
                    continue
                itemsim_mat[m1][m2] += 1/math.log(1+len(movies))

    print('build co-rated users matrix succ')

    print('calculating movie similarity matrix...')
    simfactor_count = 0
    # PRINT_STEP = 2000000

    for m1, related_movies in itemsim_mat.items():
        for m2, count in related_movies.items():
            itemsim_mat[m1][m2] = count / math.sqrt(
                movie_popular[m1] * movie_popular[m2])
            simfactor_count += 1
            # if simfactor_count % PRINT_STEP == 0:
            #     print('calculating movie similarity factor(%d)' %
            #               simfactor_count)

    print('calculate movie similarity matrix(similarity factor) succ',)
    print('Total similarity factor number = %d' %
              simfactor_count)

def recommend(user):
    K = n_sim_movie
    N = n_rec_movie
    rank = {}
    watched_movies = trainset[user]

    for movie, rating in watched_movies.items():
        for related_movie, similarity_factor in sorted(movie_sim_mat[movie].items(),
                                                           key=itemgetter(1), reverse=True)[:K]:
            if related_movie in watched_movies:
                continue
            rank.setdefault(related_movie, 0)
            rank[related_movie] += similarity_factor * rating

    return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

def evaluate():
    print('Evaluation start...')

    N = n_rec_movie
    hit = 0
    rec_count = 0
    test_count = 0
    all_rec_movies = set()
    popular_sum = 0
    for i, user in enumerate(trainset):
        test_movies = testset.get(user, {})
        rec_movies = recommend(user)
        for movie, _ in rec_movies:
            if movie in test_movies:
                hit += 1
            all_rec_movies.add(movie)
            popular_sum += math.log(1 + movie_popular[movie])
        rec_count += N
        test_count += len(test_movies)

    precision = hit / (1.0 * rec_count)
    recall = hit / (1.0 * test_count)
    coverage = len(all_rec_movies) / (1.0 * movie_count)
    popularity = popular_sum / (1.0 * rec_count)

    print ('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' %
               (precision, recall, coverage, popularity))
if __name__ == "__main__":
    generate_dataset('ratings.dat')
    generate_moviedata('movies.dat')
    print('please input your userid(>6400):')
    userid = input()
    trainset.setdefault(userid, {})
    print('please input the movieids you like,type '"s"' to stop')
    while True:
        movie = input()
        if movie == 's':
            break
        else:
            trainset[userid][movie] = 3
    print('the movies you like are:\n')
    for movieid in trainset[userid].keys():
        print(movieid, movieset[movieid], '\n')
    time.sleep(0.5)
    calc_movie_sim()
    # evaluate()
    items = recommend(str(userid))
    for key, values in items:
        print(movieset[key])

    print('please input your movieid')
    movieid=input()
    print('the movie name is :%s' % movieset[movieid])
    for movie,score in sorted(movie_sim_mat[movieid].items(),key=itemgetter(1),reverse=True)[0:10]:
        print(movieset[movie],score)
        print('\n')


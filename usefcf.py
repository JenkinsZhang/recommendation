import numpy as np
import  random
import math
import sys
from collections import defaultdict
from operator import itemgetter
import  time

movieset={}
trainset={}
testset={}
n_sim_user=30
n_rec_movie=10
user_sim_mat={}
movie_popular={}
movie_count=0

def loadfile(filename):
    fp=open(filename,'r')
    for line in (fp):
        yield line.strip('\r\n')
    fp.close()
    print('load %s succ' %filename)

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

def  calc_user_sim():
    global movie_count
    print('building movie-users inverse table...', file=sys.stderr)
    movie2users = dict()

    for user, movies in trainset.items():
        for movie in movies:
            if movie not in movie2users:
                movie2users[movie] = set()
            movie2users[movie].add(user)
            if movie not in movie_popular:
                movie_popular[movie] = 0
            movie_popular[movie] += 1
    print('build movie-users inverse table succ')

    movie_count = len(movie2users)
    print('total movie number = %d' % movie_count)

    usersim_mat = user_sim_mat
    print('generating user co-rated movies matrix...')

    for movie, users in movie2users.items():
        for u in users:
            usersim_mat.setdefault(u, defaultdict(int))
            for v in users:
                if u == v:
                    continue
                usersim_mat[u][v] += 1/math.log(1+len(users))
    print('build user co-rated movies matrix succ')

    print('calculating user similarity matrix...')
    simfactor_count = 0
    # PRINT_STEP = 2000000

    for u, related_users in usersim_mat.items():
        for v, count in related_users.items():
            usersim_mat[u][v] = count / math.sqrt(
                len(trainset[u]) * len(trainset[v]))
            simfactor_count += 1
            # if simfactor_count % PRINT_STEP == 0:
            #     print('calculating user similarity factor(%d)' %
            #             simfactor_count)

    print('calculate user similarity matrix(similarity factor) succ',
              )
    print('Total similarity factor number = %d' %
              simfactor_count)

def recommend(user):
    K = n_sim_user
    N = n_rec_movie
    rank = dict()
    watched_movies = trainset[user]

    for similar_user, similarity_factor in sorted(user_sim_mat[user].items(),
                                                      key=itemgetter(1), reverse=True)[0:K]:
        for movie in trainset[similar_user]:
            if movie in watched_movies:
                continue
            rank.setdefault(movie, 0)
            rank[movie] += similarity_factor
    return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

def generate_moviedata(filename):
    print('loading movies.dat')
    fp=open('movies.dat')
    for line in fp.readlines():
        line=line.strip('\r\t')
        movieid,moviename,moviecat=line.split('::')
        movieset[movieid]=moviename
    print('load movies.dat succ')

def evaluate():

    print ('Evaluation start...')

    N = n_rec_movie
    hit = 0
    rec_count = 0
    test_count = 0
    all_rec_movies = set()
    popular_sum = 0
    for i, user in enumerate(trainset):
        # if i % 500 == 0:
        #     print ('recommended for %d users' % i)
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

if __name__=="__main__":

    generate_dataset('ratings.dat')
    generate_moviedata('movies.dat')
    print('please input your userid(>6400):')
    userid=input()
    trainset.setdefault(userid,{})
    print('please input the movieids you like,type '"s"' to stop')
    while True:
        movie=input()
        if movie=='s':
            break
        else:
            trainset[userid][movie]=3
    print('the movies you like are:')
    for movieid in trainset[userid].keys():
        print(movieid,movieset[movieid],'\n')
    time.sleep(0.5)
    calc_user_sim()
    # evaluate()
    items = recommend(str(userid))
    for key, values in items:
        print(movieset[key])



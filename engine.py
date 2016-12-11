from flask import current_app
from progressbar import print_progress
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from time import time
import logging
import pandas
import redis


class ContentEngine(object):
    """
    Modules required:
        scipy
        scikit-learn
        pandas
        wheel
        redis
    """

    SIMKEY = 'p:smlr:%s'

    def __init__(self):
        self.log = logging.getLogger("content")
        self._r = redis.StrictRedis.from_url(current_app.config["REDIS_URL"])

    def train(self):
        training_frame = pandas.read_json(current_app.config["TRAINING_PATH"])

        # Flush the stale training data from redis
        self._r.flushdb()

        start = time()
        self._train(training_frame)
        self.log.info("training from dataset took {} s".format(time() - start))

    def _train(self, training_frame):
        hashing_vectorizer = HashingVectorizer(analyzer="word", n_features=(2 ** 30),
                                               ngram_range=(1, 3), stop_words="english")
        training_hashing_matrix = hashing_vectorizer.fit_transform(training_frame["description"])

        self.log.info("starting kernel")
        start = time()
        cosine_similarities = cosine_similarity(training_hashing_matrix, training_hashing_matrix)
        self.log.info("finished kernel. this took {} s".format(time() - start))

        self.log.info("starting adding to redis database")
        start = time()
        i = 0
        l = len(training_frame.index)
        print_progress(i, l, prefix="Progress:", suffix="Complete", bar_length=50)
        for idx, row in training_frame.iterrows():
            similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
            similar_items = [(cosine_similarities[idx][i], training_frame['id'][i]) for i in similar_indices]

            flattened = sum(similar_items[1:], ())
            self._r.zadd(self.SIMKEY % row['id'], *flattened)
            i += 1
            print_progress(i, l, prefix="Progress:", suffix="Complete", bar_length=50)
        self.log.info("finished adding {} rows to redis database. this took {} s".format(i, time() - start))

    def predict(self, id, num):
        return self._r.zrange(self.SIMKEY % id, 0, num - 1, withscores=False, desc=True)

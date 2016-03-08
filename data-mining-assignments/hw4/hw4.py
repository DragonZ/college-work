import collections, csv, random, sys, re, time, ast
from sklearn.cluster import KMeans
from numpy import linalg as LA
from scipy import spatial
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import zero_one_loss


def extract_top_2000_words(file_table):
    allwords = []
    # here traversal the first level
    for row in file_table:
        allwords += row
    top2000_words_withcount = collections.Counter(allwords).most_common()[200:2200]
    top2000words_list = []
    for row in top2000_words_withcount:
        top2000words_list.append(row[0])
    return top2000words_list


def csv_to_words_array(filename):
    # each row in file table will be one record in the original csv
    file_table = []
    with open(filename, 'rb') as file_dp:
        file_reader = csv.DictReader(file_dp)
        for row in file_reader:
            strip_reviews = re.sub('[^\w ]', '', row['text'].lower())
            file_table.append(strip_reviews.split())
    return file_table


def is_positive_label_list():
    is_positive_labels = []
    with open('stars_data.csv', 'rb') as file_dp:
        file_reader = csv.DictReader(file_dp)
        for row in file_reader:
            is_positive_labels.append(int(row['stars']))
    return is_positive_labels


def wp_wnp_review_arrays():
    wp_reviews = []
    wnp_reviews = []
    with open('stars_data.csv', 'rb') as file_dp:
        file_reader = csv.DictReader(file_dp)
        for row in file_reader:
            strip_reviews = re.sub('[^\w ]', '', row['text'].lower())
            if row['stars'] == '5':
                wp_reviews.append(strip_reviews.split())
            if row['stars'] == '1':
                wnp_reviews.append(strip_reviews.split())
    return wp_reviews, wnp_reviews


def wp_wnp_init(row_list, wp_reviews, wnp_reviews):
    wp_matrix = [[0 for x in range(2500)] for x in range(2000)]
    wnp_matrix = [[0 for x in range(2500)] for x in range(2000)]

    wp_fd = open('wp_matrix.db', 'w')
    wnp_fd = open('wnp_matrix.db', 'w')
    for i in range(2000):
        for j in range(2500):
            wp_matrix[i][j] = wp_reviews[j].count(row_list[i])
            wnp_matrix[i][j] = wnp_reviews[j].count(row_list[i])
            wp_fd.write(str(wp_matrix[i][j]) + ' ')
            wnp_fd.write(str(wnp_matrix[i][j]) + ' ')
        wp_fd.write('\n')
        wnp_fd.write('\n')
    return wp_matrix, wnp_matrix


def load_wp_wnp_from_db():
    wp_matrix = []
    wnp_matrix = []
    with open('wp_matrix.db', 'r') as fd:
        content = fd.readlines()
        i = 0
        for line in content:
            wp_matrix.append(map(int, line.split()))
            i += 1
    with open('wnp_matrix.db', 'r') as fd:
        content = fd.readlines()
        i = 0
        for line in content:
            wnp_matrix.append(map(int, line.split()))
            i += 1
    return wp_matrix, wnp_matrix


def sum_of_squares(target_list):
    return sum([i ** 2 for i in target_list])


def smooth(zero_vector):
    return [zero_vector[i] + 0.0001 for i in range(len(zero_vector))]


def normalizer(target):
    if sum(target) == 0:
        smoothed = smooth(target)
        return smoothed/LA.norm(smoothed)
    return target/LA.norm(target)


def normalize_vectors(vector_list):
    normed_vector_list = []
    for vector in vector_list:
        normed_vector_list.append(normalizer(vector))
    return normed_vector_list


def cosine_similarity(vector1, vector2):
    return 1 - spatial.distance.cosine(vector1, vector2)


def random_sample_start_centroid(source_list, sample_list):
    return [source_list[i] for i in sample_list]


def update_centroid_vectors(clusters, n_vector_list):
    new_centroids_vectors = []
    for c in clusters:
        current_centroid = [0 for i in range(len(n_vector_list[0]))]
        for i in c:
            current_centroid += n_vector_list[i]
        new_centroids_vectors.append(normalizer(current_centroid))
    return new_centroids_vectors


def spherical_k_means(n_clusters, max_iter, n_init, vector_list):
    n_vector_list = normalize_vectors(vector_list)
    best_achieved_score = 0
    best_achieved_cluster = []
    for run in range(n_init):
        # run n_init times to get best score
        # first get start centers, use index to mark all list
        print 'run ' + str(run)
        centroids = sorted(random.sample(xrange(len(n_vector_list)), n_clusters))
        centroids_vectors = random_sample_start_centroid(n_vector_list, centroids)
        clusters = []
        for c in centroids:
            clusters.append([])
        last_one_iter_score = 0
        for i in range(max_iter):
            # run at most max_iteration, may stop early
            # TODO: may need to norm centroid here
            if i > 0:
                # need to update centroid vectors here
                centroids_vectors = update_centroid_vectors(clusters, n_vector_list)
                clusters = []
                for c in centroids_vectors:
                    clusters.append([])
            for v in range(len(n_vector_list)):
                current_best_score = -1.0
                current_cluster_num = -1
                for cv_index in range(n_clusters):
                    similarity = cosine_similarity(centroids_vectors[cv_index], n_vector_list[v])
                    if similarity > current_best_score:
                        # this cluster is more fit
                        current_best_score = similarity
                        current_cluster_num = cv_index
                if current_cluster_num == -1:
                    print 'error: fit cluster not found'
                else:
                    clusters[current_cluster_num].append(v)
            # TODO: after all clustered, need current score
            # TODO: if score is good enough, break
            current_one_iter_score = 0
            for c in range(len(clusters)):
                for v in clusters[c]:
                    current_one_iter_score += cosine_similarity(n_vector_list[v], centroids_vectors[c])
            if abs(current_one_iter_score - last_one_iter_score) < 0.0001:
                break
            else:
                last_one_iter_score = current_one_iter_score
        if last_one_iter_score > best_achieved_score:
            best_achieved_score = last_one_iter_score
            best_achieved_cluster = clusters
    return best_achieved_score, best_achieved_cluster


def k_means_label_to_cluster(label_list, n_cluster):
    clusters = []
    for i in range(n_cluster):
        clusters.append([])
    for label_i in range(len(label_list)):
        clusters[label_list[label_i]].append(label_i)
    return clusters


def review_contains(review, one_cluster, top_2000_dict):
    for word in review:
        if top_2000_dict.has_key(word):
            index_of_word = top_2000_dict[word]
        else:
            index_of_word = -1
        if index_of_word in one_cluster:
            return True
    return False


def new_100_feature(all_reviews_list, top_2000_words_list, clusters_wp, clusters_wnp, top_2000_dict):
    new_100_feature_matrix = [[0 for x in range(100)] for x in range(5000)]
    for i in range(5000):
        print 'start => ' + str(i) + 'th review'
        for j in range(100):
            if j < 50:
                if review_contains(all_reviews_list[i], clusters_wp[j], top_2000_dict):
                    new_100_feature_matrix[i][j] = 1
                else:
                    new_100_feature_matrix[i][j] = 0
            else:
                if review_contains(all_reviews_list[i], clusters_wnp[j-50], top_2000_dict):
                    new_100_feature_matrix[i][j] = 1
                else:
                    new_100_feature_matrix[i][j] = 0
        print 'finish => ' + str(i) + 'th review'
    return new_100_feature_matrix


def load_100_feature_list_from(filename):
    with open(filename, 'r') as fd:
        data = ast.literal_eval(fd.read())
        return data


def translate_human_readable_cluster(clusters, look_up_dict):
    counter = 1
    for one_cluster in clusters:
        sys.stdout.write(str(counter) + ' => ')
        for index in one_cluster:
            sys.stdout.write(look_up_dict[index] + ', ')
        sys.stdout.write('\n')
        counter += 1


def complete_alert():
    sys.stdout.write('\a')
    sys.stdout.write('\a')
    sys.stdout.write('\a')
    sys.stdout.flush()


def multiple_pop(target_list, target_label_list, pop_num):
    poped = []
    poped_label = []
    for p_time in range(pop_num):
        p_index = random.sample(range(len(target_list)), 1)
        poped.append(target_list.pop(p_index[0]))
        poped_label.append(target_label_list.pop(p_index[0]))
    return poped, poped_label, target_list, target_label_list


def random_word_binary_feature_array(top_word_list):
    random_100 = random.sample(top_word_list, 100)
    all_reviews = csv_to_words_array('stars_data.csv')
    word_100_feature_matrix = [[0 for x in range(100)] for x in range(5000)]
    for i in range(5000):
        for j in range(100):
            if random_100[j] in all_reviews[i]:
                word_100_feature_matrix[i][j] = 1
            else:
                word_100_feature_matrix[i][j] = 0
    return word_100_feature_matrix


def join_two_feature_matrix(m1, m2):
    new_matrix = []
    for i in range(5000):
        new_matrix.append(m1[i]+m2[i])
    return new_matrix

# only need once to get top 2000 words
# all_reviews = csv_to_words_array('stars_data.csv')
# top_2000_words = extract_top_2000_words(all_reviews)
# top_word_database = open('top_word.db', 'w')
# for word in top_2000_words:
#     top_word_database.write(word + ' ')


top_word_database = open('top_word.db', 'r')
top_2000_features = top_word_database.read().split()
# try to optimize search speed
top_2000_dict = {}
for word_index in range(2000):
    top_2000_dict[top_2000_features[word_index]] = word_index

all_reviews = csv_to_words_array('stars_data.csv')
wp_reviews_array, wnp_reviews_array = wp_wnp_review_arrays()

# only need to compute wp and wnp once
# current = time.time()
# wp, wnp = wp_wnp_init(top_2000_features, wp_reviews_array, wnp_reviews_array)
# print("--- %s seconds ---" % (time.time() - current))
wp, wnp = load_wp_wnp_from_db()

# s_k_means for new binary feature construction
# print 'start skmeans wp cluster'
# wp_cluster_score, wp_clusters = spherical_k_means(50, 100, 2, wp)
# print 'finish skmeans wp cluster'
# print 'start skmeans wNp cluster'
# wnp_cluster_score, wnp_clusters = spherical_k_means(50, 100, 2, wnp)
# print 'finish skmeans wNp cluster'
# print 'wp_cluster_score => ' + str(wp_cluster_score)
# print 'wnp_cluster_score => ' + str(wnp_cluster_score)

# Q1-a
# for k in [10, 20, 50, 100, 200]:
#     standard_k_means = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=30)
#     standard_k_means.fit(wnp)
#     print standard_k_means.inertia_

# Q1-b
# standard_k_means = KMeans(n_clusters=200, init='k-means++', max_iter=100, n_init=30)
# standard_k_means.fit(wp)
# wp_clusters = k_means_label_to_cluster(standard_k_means.labels_.tolist(), 200)
# standard_k_means.fit(wnp)
# wnp_clusters = k_means_label_to_cluster(standard_k_means.labels_.tolist(), 200)
# translate_human_readable_cluster(wp_clusters, top_2000_features)
# print '************************************************************************'
# translate_human_readable_cluster(wnp_clusters, top_2000_features)

# Q1-c
# for k in [10, 20, 50, 100, 200]:
#     skm_score, cl = spherical_k_means(k, 100, 2, wnp)
#     print skm_score
# skm_score, cl = spherical_k_means(200, 100, 1, wp)
# translate_human_readable_cluster(cl, top_2000_features)
# skm_score, cl = spherical_k_means(200, 100, 1, wnp)
# translate_human_readable_cluster(cl, top_2000_features)


nbc = MultinomialNB()
for rep in range(10):
    # new_feature_list = load_100_feature_list_from('100_new_feature_sk.db')
    new_feature_list = join_two_feature_matrix(random_word_binary_feature_array(top_2000_features), load_100_feature_list_from('100_new_feature.db'))
    is_positive_list = is_positive_label_list()
    test_set, test_set_true_label, new_feature_list, is_positive_list = multiple_pop(new_feature_list, is_positive_list, 500)
    print str(rep) + 'experiment here =====> '
    for tss in [100, 250, 500, 1000, 2000]:
        training_set, training_set_label, temp, templ = multiple_pop(new_feature_list, is_positive_list, tss)
        nbc.fit(training_set, training_set_label)
        predict_label = nbc.predict(test_set)
        print str(zero_one_loss(test_set_true_label, predict_label))







# k_means new binary feature construction
# standard_k_means = KMeans(n_clusters=50, init='k-means++', max_iter=100, n_init=30)
# standard_k_means.fit(wp)
# wp_clusters = k_means_label_to_cluster(standard_k_means.labels_.tolist(), 50)
# standard_k_means.fit(wnp)
# wnp_clusters = k_means_label_to_cluster(standard_k_means.labels_.tolist(), 50)


# new_100 = new_100_feature(all_reviews, top_2000_features, wp_clusters, wnp_clusters, top_2000_dict)
# print new_100


# print len(standard_k_means.labels_.tolist())
# print standard_k_means.labels_.tolist()

# f1 = open('test1', 'w')
# f2 = open('test2', 'w')
# for w in wp[0]:
#     f1.write(str(w))
# for w in t1[0]:
#     f2.write(w)

# print 'start k means ...'
# current = time.time()

# print("--- %s seconds ---" % (time.time() - current))
# maybe later need to save wp and wnp to save time
# current = time.time()
# print("--- %s seconds ---" % (time.time() - current))

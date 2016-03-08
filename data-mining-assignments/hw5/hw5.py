import collections, csv, random, sys, re, time, ast, pickle, operator
from scipy import stats

def extract_top_2000_words(file_table):
    allwords = []
    # here traversal the first level
    for row in file_table:
        allwords += row
    top2000_words_withcount = collections.Counter(allwords).most_common()[100:2100]
    top2000words_list = []
    for row in top2000_words_withcount:
        top2000words_list.append(row[0])
    return top2000words_list

def csv_to_words_array():
    # each row in file table will be one record in the original csv
    file_table = []
    with open('stars_data.csv', 'rb') as file_dp:
        file_reader = csv.DictReader(file_dp)
        for row in file_reader:
            strip_reviews = re.sub('[^\w ]', '', row['text'].lower())
            file_table.append(strip_reviews.split())
    return file_table

def generate_feature_matrix(top2000words_features):
    feature_matrix = []
    with open('stars_data.csv', 'rb') as file_dp:
        file_reader = csv.DictReader(file_dp)
        for row in file_reader:
            strip_reviews = re.sub('[^\w ]', '', row['text'].lower())
            current_review_word_list = strip_reviews.split()
            current_attributes = []
            for x in range(0, 2000):
            	if top2000words_features[x] in current_review_word_list:
            		current_attributes.append(1)
            	else:
            		current_attributes.append(0)
            # label order = ispositive, isnegative
            if row['stars'] == '5':
                current_attributes.append(1)
                current_attributes.append(0)
            if row['stars'] == '1':
                current_attributes.append(0)
                current_attributes.append(1)
            feature_matrix.append(current_attributes)
    return feature_matrix

def help_feature_present_table(word_feature_list, target_matrix):
	feature_present_table = {}
	for i in range(0, 2002):
		current_feature_present_in = []
		for j in range(0, 5000):
			if target_matrix[j][i] == 1:
				current_feature_present_in.append(j)
		if i < 2000:
			feature_present_table[word_feature_list[i]] = current_feature_present_in
		elif i == 2000:
			feature_present_table['isPositive'] = current_feature_present_in
		else:
			feature_present_table['isNegative'] = current_feature_present_in
	return feature_present_table

def gen_size1_itemset(feature_present_table, sthreadhold):
	itemset = {}
	for key in feature_present_table:
		if len(feature_present_table[key])/5000.0 >= sthreadhold:
			itemset[key] = len(feature_present_table[key])
	return itemset

def gen_size2_itemset(size1_itemset, feature_present_table, sthreadhold):
	itemset = {}
	ordered_key_pairs = []
	num_size1_itemset = len(size1_itemset)
	keys_size1_itemset = size1_itemset.keys()
	for i in range(num_size1_itemset):
		for j in range(i+1, num_size1_itemset):
			self_join_count = len(collections.Counter(feature_present_table[keys_size1_itemset[i]]) & \
				collections.Counter(feature_present_table[keys_size1_itemset[j]]))
			if self_join_count/5000.0 >= sthreadhold:
				key_pair = []
				itemset[keys_size1_itemset[i] + ' ' + keys_size1_itemset[j]] = self_join_count
				key_pair.append(keys_size1_itemset[i])
				key_pair.append(keys_size1_itemset[j])
				ordered_key_pairs.append(key_pair)
	return itemset, ordered_key_pairs

def qualified_size3_key_combination(key_pairs_from_size2):
	num_pairs_from_size2 = len(key_pairs_from_size2)
	qualified_pairs = []
	for i in range(num_pairs_from_size2):
		for j in range(i+1, num_pairs_from_size2):
			if key_pairs_from_size2[i][0] == key_pairs_from_size2[j][0] and \
			[key_pairs_from_size2[i][1], key_pairs_from_size2[j][1]] in key_pairs_from_size2:
				key_pair = []
				key_pair.append(key_pairs_from_size2[i][0])
				key_pair.append(key_pairs_from_size2[i][1])
				key_pair.append(key_pairs_from_size2[j][1])
				qualified_pairs.append(key_pair)
			if key_pairs_from_size2[i][0] != key_pairs_from_size2[j][0]:
				break
	return qualified_pairs

def gen_size3_itemset(key_combinaton_candidate, feature_present_table, sthreadhold):
	itemset = {}
	for key_combinaton in key_combinaton_candidate:
		candidate_count = len(collections.Counter(feature_present_table[key_combinaton[0]]) & \
			collections.Counter(feature_present_table[key_combinaton[1]]) & \
			collections.Counter(feature_present_table[key_combinaton[2]]))
		if candidate_count/5000.0 >= sthreadhold:
			itemset[key_combinaton[0] + ' ' + key_combinaton[1] + ' ' + key_combinaton[2]] = candidate_count
	return itemset

def gen_size2_rules(size1_itemset, size2_itemset, cthreadhold):
	rule_set = {}
	for key in size2_itemset:
		key_list = key.split()
		# compute first -> second 
		first_to_second = float(size2_itemset[key])/float(size1_itemset[key_list[0]])
		if first_to_second >= cthreadhold:
			current_rule_detail = key
			rule_set[current_rule_detail] = first_to_second
		# compute second -> first 
		second_to_first = float(size2_itemset[key])/float(size1_itemset[key_list[1]])
		if second_to_first >= cthreadhold:
			current_rule_detail = key_list[1] + ' ' + key_list[0]
			rule_set[current_rule_detail] = second_to_first
	return rule_set

def gen_size3_rules(size2_itemset, size3_itemset, cthreadhold):
	rule_set = {}
	for key in size3_itemset:
		key_list = key.split()
		# 0, 1, 2
		# compute 0, 1 -> 2
		p01_to_2 = float(size3_itemset[key])/float(size2_itemset[key_list[0]+' '+key_list[1]])
		if p01_to_2 >= cthreadhold:
			rule_set[key_list[0]+' '+key_list[1]+' '+key_list[2]] = p01_to_2
		# compute 0, 2 -> 1
		p02_to_1 = float(size3_itemset[key])/float(size2_itemset[key_list[0]+' '+key_list[2]])
		if p02_to_1 >= cthreadhold:
			rule_set[key_list[0]+' '+key_list[2]+' '+key_list[1]] = p02_to_1
		# compute 1, 2 -> 0
		p12_to_0 = float(size3_itemset[key])/float(size2_itemset[key_list[1]+' '+key_list[2]])
		if p12_to_0 >= cthreadhold:
			rule_set[key_list[1]+' '+key_list[2]+' '+key_list[0]] = p12_to_0
	return rule_set

def gen_size2_rules_chi(size1_itemset, size2_itemset, chithreadhold):
	rule_set = {}
	for item in size2_itemset:
		A = item.split()[0]
		B = item.split()[1]
		a = size2_itemset[item]
		b = size1_itemset[A]-size2_itemset[item]
		c = size1_itemset[B]-size2_itemset[item]
		d = 5000 - a - b - c
		target_matrix = [[a, b], [c ,d]]
		chi_score, p, trash1, trash2 = stats.chi2_contingency(target_matrix)
		if p < chithreadhold:
			rule_set[item] = [chi_score, p]
			# rule_set[B + ' ' + A] = [chi_score, p]
	return rule_set

def gen_size3_rules_chi(size1_itemset, size2_itemset, size3_itemset, chithreadhold):
	rule_set = {}
	for item in size3_itemset:
		A = item.split()[0]
		B = item.split()[1]
		C = item.split()[2]
		AB = A + ' ' + B
		AC = A + ' ' + C
		BC = B + ' ' + C
		# AB -> C
		a = size3_itemset[item]
		b = size2_itemset[AB] - a
		c = size1_itemset[C] - a
		d = 5000 - a - b - c
		target_matrix = [[a, b], [c ,d]]
		chi_score, p, trash1, trash2 = stats.chi2_contingency(target_matrix)
		if p < chithreadhold:
			rule_set[item] = [chi_score, p]
		# AC -> B
		a = size3_itemset[item]
		b = size2_itemset[AC] - a
		c = size1_itemset[B] - a
		d = 5000 - a - b - c
		target_matrix = [[a, b], [c ,d]]
		chi_score, p, trash1, trash2 = stats.chi2_contingency(target_matrix)
		if p < chithreadhold:
			rule_set[AC + ' ' + B] = [chi_score, p]
		# BC -> A
		a = size3_itemset[item]
		b = size2_itemset[BC] - a
		c = size1_itemset[A] - a
		d = 5000 - a - b - c
		target_matrix = [[a, b], [c ,d]]
		chi_score, p, trash1, trash2 = stats.chi2_contingency(target_matrix)
		if p < chithreadhold:
			rule_set[BC + ' ' + A] = [chi_score, p]
	return rule_set

def find_size2_support(keys, size2_itemset):
	cand1 = keys[0] + ' ' + keys[1]
	cand2 = keys[1] + ' ' + keys[0]
	if cand1 in size2_itemset:
		return size2_itemset[cand1]
	else:
		return size2_itemset[cand2]

def find_size3_support(keys, size3_itemset):
	cand1 = keys[0] + ' ' + keys[1] + ' ' + keys[2]
	cand2 = keys[0] + ' ' + keys[2] + ' ' + keys[1]
	cand3 = keys[2] + ' ' + keys[0] + ' ' + keys[1]
	if cand1 in size3_itemset:
		return size3_itemset[cand1]
	elif cand2 in size3_itemset:
		return size3_itemset[cand2]
	else:
		return size3_itemset[cand3]

support_threadhold = 0.03
confidence_threadhold = 0.25
chi_threadhold = 0.05
ordered_2000_feature_list = extract_top_2000_words(csv_to_words_array())
target_feature_matrix = generate_feature_matrix(ordered_2000_feature_list)

feature_present_table = help_feature_present_table(ordered_2000_feature_list, target_feature_matrix)
size1_qualified_itemset = gen_size1_itemset(feature_present_table, support_threadhold)
size2_qualified_itemset, key_pairs_for_size3 = gen_size2_itemset(size1_qualified_itemset, feature_present_table, support_threadhold)
possible_size3_key_combination = qualified_size3_key_combination(key_pairs_for_size3)
size3_qualified_itemset = gen_size3_itemset(possible_size3_key_combination, feature_present_table, support_threadhold)


size2_rules = gen_size2_rules(size1_qualified_itemset, size2_qualified_itemset, confidence_threadhold)
size3_rules = gen_size3_rules(size2_qualified_itemset, size3_qualified_itemset, confidence_threadhold)

# chi_threadhold = chi_threadhold/(len(size2_qualified_itemset)*2 + len(size3_qualified_itemset)*3)
# size2_rules = gen_size2_rules_chi(size1_qualified_itemset, size2_qualified_itemset, chi_threadhold)
# size3_rules = gen_size3_rules_chi(size1_qualified_itemset, size2_qualified_itemset, size3_qualified_itemset, chi_threadhold)

all_rules = size2_rules.items() + size3_rules.items()
sorted_rules = sorted(all_rules, key=operator.itemgetter(1), reverse=True)

# print len(size2_rules)
# print len(size3_rules)

# all_rules = []
# for rule in size2_rules:
# 	tr = [rule]
# 	tr += size2_rules[rule]
# 	all_rules.append(tr)
# for rule in size3_rules:
# 	tr = [rule]
# 	tr += size3_rules[rule]
# 	all_rules.append(tr)
# sorted_rules = sorted(all_rules, key=operator.itemgetter(2))


top30 = 1
for line in sorted_rules:
	if top30 > 30:
		break
	print line[0]
	# keys = line[0].split()
	# key_size = len(keys)
	# rule_string = 't'
	# support = 0.0
	# if key_size == 2:
	# 	rule_string = 'IF ' + keys[0] + ' THEN ' + keys[1]
	# 	support = find_size2_support(keys, size2_qualified_itemset)/5000.0
	# if key_size == 3:
	# 	rule_string = 'IF ' + keys[0] + ' AND ' + keys[1] + ' THEN ' + keys[2]
	# 	support = find_size3_support(keys, size3_qualified_itemset)/5000.0
	# print top30, ' & ', rule_string, ' & $', line[2], '$ & $', line[1], '$ & $', support, '$ \\\\'
	top30 += 1








# pickle.dump(target_feature_matrix, open("target_matrix.db", "wb"))
# target_feature_matrix = pickle.load(open("target_matrix.db", "rb"))



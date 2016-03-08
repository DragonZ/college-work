import collections, csv, random, sys, re

def extractTop2000Words(file_table):
	allwords = []
	# here taversal the first level 
	for row in file_table:
		allwords += row
	top2000_words_withcount = collections.Counter(allwords).most_common()[200:2199]
	top2000words_list = []
	for row in top2000_words_withcount:
		top2000words_list.append(row[0])
	return top2000words_list

def csvToWordsArray(filename):
	# each row in file table will be one record in the original csv
	file_table = []
	with open(filename, 'rb') as file_dp:
		file_reader = csv.DictReader(file_dp)
		for row in file_reader:
			strip_reviews = re.sub('[^\w ]','',row['text'].lower())
			file_table.append(strip_reviews.split())
	return file_table

def csvLabelArray(filename, label_num):
	# although it looks lile num, label are string 
	# label_num = 5, funny
	# label_num = 7, stars
	labelarray = []
	with open(filename, 'rb') as file_dp:
		file_reader = csv.DictReader(file_dp)
		for row in file_reader:
			if label_num == 5:
				labelarray.append(row['funny'])
			if label_num == 7:
				labelarray.append(row['stars'])
		return labelarray

def funnyConditionalTables(review_words_list, top2000words, label_list):
	alltables = []
	for word in top2000words:
		single_table = []
		x = 0
		y = 0
		for i in range(len(review_words_list)):
			if label_list[i] == '0' and word in review_words_list[i]:
				# label no funny, has word yes, (0,1)
				x += 1
			if label_list[i] != '0' and word in review_words_list[i]:
				# (1, 1) 
				y += 1
		single_table.append(x)
		single_table.append(y)
		alltables.append(single_table)
	return alltables

def predictFunny(test_review_list, lookup, label_no, label_yes, top2000words):
	# predict funny
	allprediction = []
	for record in test_review_list:
		multiple_list_yes = float(label_yes)/(label_yes+label_no)
		multiple_list_no = float(label_no)/(label_yes+label_no)
		for i in range(len(top2000words)):
			if top2000words[i] in record:
				# this review has this word
				if lookup[i][1] == 0:
					multiple_list_yes *= float(lookup[i][1]+1)/(label_yes+2)
				else:
					multiple_list_yes *= float(lookup[i][1])/label_yes

				if lookup[i][0] == 0:
					multiple_list_no *= float(lookup[i][0]+1)/(label_no+2)
				else:
					multiple_list_no *= float(lookup[i][0])/label_no
			else:
				if label_yes == lookup[i][1]:
					multiple_list_yes *= float(1)/(label_yes+2)
				else:
					multiple_list_yes *= float(label_yes-lookup[i][1])/label_yes

				if label_no == lookup[i][0]:
					multiple_list_no *= float(1)/(label_no+2)
				else:
					multiple_list_no *= float(label_no-lookup[i][0])/label_no
		if multiple_list_yes > multiple_list_no:
			allprediction.append('1')
		else:
			allprediction.append('0')
		
	return allprediction

def funnyPredictionScore(prediction, true_re):
	count = 0
	for i in range(len(prediction)):
		if prediction[i] == '0' and true_re[i] > '0':
			count += 1
		if prediction[i] > '0' and true_re[i] == '0':
			count += 1
	return float(count)/len(prediction)

def starsConditionalTables(review_words_list, top2000words, label_list):
	alltables = []
	for word in top2000words:
		single_table = []
		x = 0
		y = 0
		for i in range(len(review_words_list)):
			if label_list[i] == '1' and word in review_words_list[i]:
				# label no/bad star, has word yes, (0,1)
				x += 1
			if label_list[i] == '5' and word in review_words_list[i]:
				# (1, 1) 
				y += 1
		single_table.append(x)
		single_table.append(y)
		alltables.append(single_table)
	return alltables

def predictStars(test_review_list, lookup, label_no, label_yes, top2000words):
	# predict funny
	allprediction = []
	for record in test_review_list:
		multiple_list_yes = float(label_yes)/(label_yes+label_no)
		multiple_list_no = float(label_no)/(label_yes+label_no)
		for i in range(len(top2000words)):
			if top2000words[i] in record:
				# this review has this word
				if lookup[i][1] == 0:
					multiple_list_yes *= float(lookup[i][1]+1)/(label_yes+2)
				else:
					multiple_list_yes *= float(lookup[i][1])/label_yes

				if lookup[i][0] == 0:
					multiple_list_no *= float(lookup[i][0]+1)/(label_no+2)
				else:
					multiple_list_no *= float(lookup[i][0])/label_no
			else:
				if label_yes == lookup[i][1]:
					multiple_list_yes *= float(1)/(label_yes+2)
				else:
					multiple_list_yes *= float(label_yes-lookup[i][1])/label_yes

				if label_no == lookup[i][0]:
					multiple_list_no *= float(1)/(label_no+2)
				else:
					multiple_list_no *= float(label_no-lookup[i][0])/label_no
		if multiple_list_yes > multiple_list_no:
			allprediction.append('5')
		else:
			allprediction.append('1')
		
	return allprediction

def starsPredictionScore(prediction, true_re):
	count = 0
	for i in range(len(prediction)):
		if prediction[i] != true_re[i]:
			count += 1
	return float(count)/len(prediction)

def outputTopWords(top2000words, num_to_output):
	for i in xrange(1,num_to_output*10+1):
		print 'WORD'+str(i)+' '+top2000words[i-1]



trainingdataset = csvToWordsArray(sys.argv[1])
top2000words_in_training = extractTop2000Words(trainingdataset)
testdataset = csvToWordsArray(sys.argv[2])
outputTopWords(top2000words_in_training, int(sys.argv[4]))
# need for each top word (2000), there is 2*2 matrix, format: 
# no [no, yes] yes [no, yes] (2D=>1D), indeed we just need two
# print float(5)/2

if sys.argv[3] == '5':
	# print 'funny'
	trainingdataset_label = csvLabelArray(sys.argv[1], 5)
	label_no_num = collections.Counter(trainingdataset_label)['0']
	label_yes_num = len(trainingdataset_label) - label_no_num
	learning_lookup = funnyConditionalTables(trainingdataset, top2000words_in_training, trainingdataset_label)
	predicting_result = predictFunny(testdataset, learning_lookup, label_no_num, label_yes_num, top2000words_in_training)
	true_result = csvLabelArray(sys.argv[2], 5)
	sys.stdout.write('ZERO-ONE-LOSS ')
	print funnyPredictionScore(predicting_result, true_result)
elif sys.argv[3] == '7':
	# print 'stars'
	trainingdataset_label = csvLabelArray(sys.argv[1], 7)
	label_no_num = collections.Counter(trainingdataset_label)['1']
	label_yes_num = collections.Counter(trainingdataset_label)['5']
	learning_lookup = starsConditionalTables(trainingdataset, top2000words_in_training, trainingdataset_label)
	predicting_result = predictStars(testdataset, learning_lookup, label_no_num, label_yes_num, top2000words_in_training)
	true_result = csvLabelArray(sys.argv[2], 7)
	sys.stdout.write('ZERO-ONE-LOSS ')
	print starsPredictionScore(predicting_result, true_result)
else:
	print 'wrong'





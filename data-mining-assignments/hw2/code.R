Q1
	a)
	yelp_dat = read.csv("~/Dropbox/Spring2015/CS573/hw/yelp.dat", header=TRUE, sep=";")
	yelp_num_col = yelp_dat[sapply(yelp_dat, is.numeric)]
	yelp_principal_component_analysis = princomp(yelp_num_col)
	b)
	plot(yelp_principal_component_analysis)
	summary(yelp_principal_component_analysis)
	c)
	yelp_principal_component_analysis$loadings
	d)
	yelp_with_logReview = yelp_num_col
	yelp_with_logReview[2] = log(yelp_num_col[2])
	yelp_logRC_PCA = princomp(yelp_with_logReview)
	plot(yelp_logRC_PCA)
	summary(yelp_logRC_PCA)
	yelp_logRC_PCA$loadings
	e)
	yelp_random100 = yelp_num_col[sample(nrow(yelp_num_col), 100), ]
	yelp_r100_PCA = princomp(yelp_random100)
	plot(yelp_r100_PCA)
	summary(yelp_r100_PCA)
	yelp_r100_PCA$loadings
	yelp_random100_logR = yelp_random100
	yelp_random100_logR[2] = log(yelp_random100[2])
	yelp_r100_logR_PCA = princomp(yelp_random100_logR)
	plot(yelp_r100_logR_PCA)
	summary(yelp_r100_logR_PCA)
	yelp_r100_logR_PCA$loadings

Q2
	a)
	yelp_subset_RCTC = yelp_dat[, cbind("review_count", "tip_count")]
	yelp_subset_RCTC_PCA = princomp(yelp_subset_RCTC)
	yelp_subset_RCTC_PCA$loadings
	summary(yelp_subset_RCTC_PCA)

	b)
	mean_center_subset = scale(yelp_subset_RCTC, center=TRUE, scale=FALSE)
	vMatrix = matrix(, nrow = 2, ncol = 39)
	for (i in -19:19) { vMatrix[1, i+20] = i*0.05
	vMatrix[2, i+20] = (1 - vMatrix[1, i+20]^2)^0.5}
	View(vMatrix)
	projection_matrix = mean_center_subset %*% vMatrix
	View(projection_matrix)
	var_matrix = matrix(, nrow = 2, ncol = 39)
	for (i in -19:19) { var_matrix[1, i+20] = i*0.05
	var_matrix[2, i+20] = var(projection_matrix[, i+20])}
	View(var_matrix)
	plot(var_matrix[1,], var_matrix[2,], main="v1-score relation")

Q3
	a)
	ccol <- yelp_dat$categories
	ccol_list_type = strsplit(as.character(ccol), ",")
	all_values_nu = unlist(ccol_list_type)
	sorted_category_list = sort(table(all_values_nu), decreasing = TRUE)
	top30_category = sorted_category_list[1:30]
	print(top30_category)
	category_binary_feature_matrix = matrix(, nrow=14191, ncol = 30)
	for ( i in 1:30) {
	for (j in 1:14191) {
		
		if (grepl(names(top30_category)[i], ccol[j], fixed=TRUE))
			category_binary_feature_matrix[j, i] = 1
		else
			category_binary_feature_matrix[j, i] = 0
		
	}
	}
	View(category_binary_feature_matrix)
	colnames(category_binary_feature_matrix) <- names(top30_category)

	b)
	city_col <- yelp_dat$city
	all_city_nu = unlist(city_col)
	sorted_city_list = sort(table(all_city_nu), decreasing = TRUE)
	top30_city = sorted_city_list[1:30]
	city_binary_feature_matrix = matrix(, nrow=14191, ncol = 30)
	for ( i in 1:30) {
	for (j in 1:14191) {
		if (grepl(names(top30_city)[i], city_col[j]))
			city_binary_feature_matrix[j, i] = 1
		else
			city_binary_feature_matrix[j, i] = 0
		}
	}
	colnames(city_binary_feature_matrix) <- names(top30_city)

	c)
	all_binary_feature_matrix = matrix(, nrow = 60, ncol = 60)
	for (i in 1:60) {
		for (j in 1:60) {
			all_binary_feature_matrix[i, j] = 0
		}
	}
	for (m in 1:14191) {
		for (i in 1:30) {
			for (j in 1:30) {
				if (city_binary_feature_matrix[m, i] == 0 && category_binary_feature_matrix[m, j] == 0)
				{
					all_binary_feature_matrix[j*2-1, i*2-1] = all_binary_feature_matrix[j*2-1, i*2-1] + 1
				}
				else if (city_binary_feature_matrix[m, i] == 0 && category_binary_feature_matrix[m, j] == 1)
				{
					all_binary_feature_matrix[j*2, i*2-1] = all_binary_feature_matrix[j*2, i*2-1] + 1
				}
				else if (city_binary_feature_matrix[m, i] == 1 && category_binary_feature_matrix[m, j] == 0)
				{
					all_binary_feature_matrix[j*2-1, i*2] = all_binary_feature_matrix[j*2-1, i*2] + 1
				}
				else if (city_binary_feature_matrix[m, i] == 1 && category_binary_feature_matrix[m, j] == 1)
				{
					all_binary_feature_matrix[j*2, i*2] = all_binary_feature_matrix[j*2, i*2] + 1
				}
			}
		}
	}
	city_names = names(top30_city)
	category_names = names(top30_category)
	all_binary_feature_score = matrix(, nrow = 900, ncol = 4)
	temp_matrix = matrix(, nrow = 2, ncol = 2)
	for (i in 1:30) {
			for (j in 1:30) {
				
				temp_matrix[1,1] = all_binary_feature_matrix[j*2-1, i*2-1]
				temp_matrix[1,2] = all_binary_feature_matrix[j*2-1, i*2]
				temp_matrix[2,1] = all_binary_feature_matrix[j*2, i*2-1]
				temp_matrix[2,2] = all_binary_feature_matrix[j*2, i*2]
				result = chisq.test(temp_matrix)
				m = (i-1)*30+j
				all_binary_feature_score[m, 1] = result$statistic
				all_binary_feature_score[m, 2] = result$p.value
				all_binary_feature_score[m, 3] = city_names[i]
				all_binary_feature_score[m, 4] = category_names[j]
				
			}
		}
	all_binary_feature_score_ordered = all_binary_feature_score[order(as.numeric(all_binary_feature_score[, 1]), decreasing=TRUE), ]

	d)
	all_info_matrix = matrix(, nrow=25, ncol=10)
	temp_matrix = matrix(, nrow = 2, ncol = 2)
	for (i in 1:10) { all_info_matrix[1, i] = 2^(i+3)
		for (j in 1:10) {
			sample_data = yelp_dat[sample(nrow(yelp_dat), 2^(i+3)), ]
			temp_matrix[1,1] = nrow(subset(sample_data, !grepl(" Coffee & Tea", sample_data$categories, fixed=TRUE) & !grepl(" Edinburgh", sample_data$city, fixed=TRUE)))
			temp_matrix[1,2] = nrow(subset(sample_data, !grepl(" Coffee & Tea", sample_data$categories, fixed=TRUE) & grepl(" Edinburgh", sample_data$city, fixed=TRUE)))
			temp_matrix[2,1] = nrow(subset(sample_data, grepl(" Coffee & Tea", sample_data$categories, fixed=TRUE) & !grepl(" Edinburgh", sample_data$city, fixed=TRUE)))
			temp_matrix[2,2] = nrow(subset(sample_data, grepl(" Coffee & Tea", sample_data$categories, fixed=TRUE) & grepl(" Edinburgh", sample_data$city, fixed=TRUE)))
			result = chisq.test(temp_matrix)
			m = j+1
			if(is.nan(result$statistic))
				all_info_matrix[m, i] = 0
			else
				all_info_matrix[m, i] = result$statistic


			temp_matrix[1,1] = nrow(subset(sample_data, !grepl(" Bars", sample_data$categories, fixed=TRUE) & !grepl(" Glendale", sample_data$city, fixed=TRUE)))
			temp_matrix[1,2] = nrow(subset(sample_data, !grepl(" Bars", sample_data$categories, fixed=TRUE) & grepl(" Glendale", sample_data$city, fixed=TRUE)))
			temp_matrix[2,1] = nrow(subset(sample_data, grepl(" Bars", sample_data$categories, fixed=TRUE) & !grepl(" Glendale", sample_data$city, fixed=TRUE)))
			temp_matrix[2,2] = nrow(subset(sample_data, grepl(" Bars", sample_data$categories, fixed=TRUE) & grepl(" Glendale", sample_data$city, fixed=TRUE)))
			result = chisq.test(temp_matrix)
			m = j+13
			if(is.nan(result$statistic))
				all_info_matrix[m, i] = 0
			else
				all_info_matrix[m, i] = result$statistic
			}
			all_info_matrix[12, i] = mean(all_info_matrix[2:11, i])
			all_info_matrix[13, i] = sd(all_info_matrix[2:11, i])

			all_info_matrix[24, i] = mean(all_info_matrix[14:23, i])
			all_info_matrix[25, i] = sd(all_info_matrix[14:23, i])
		}
		install.packages("Hmisc", dependencies=T)
		library("Hmisc")
		max_dots = data.frame(
  			x  = all_info_matrix[1, ]
  			, y  = all_info_matrix[12, ]
  			, sd = all_info_matrix[13, ]
		)
		good_dots = data.frame(
  			x  = all_info_matrix[1, ]
  			, y  = all_info_matrix[24, ]
  			, sd = all_info_matrix[25, ]
		)
		plot(max_dots$x, max_dots$y, ylim=c(0,400), type="l", col="red", xlab="sample size", ylab="mean with sd_range", main="Amax Agood Experiment")
		epsilon = 40
		for(i in 1:10) {
    		up = max_dots$y[i] + max_dots$sd[i]
    		low = max_dots$y[i] - max_dots$sd[i]
    		segments(max_dots$x[i],low , max_dots$x[i], up)
    		segments(max_dots$x[i]-epsilon, up , max_dots$x[i]+epsilon, up)
    		segments(max_dots$x[i]-epsilon, low , max_dots$x[i]+epsilon, low)
		}
		par(new=TRUE)
		plot(good_dots$x, good_dots$y, ylim=c(0,400), type="l", col="blue", xlab="", ylab="")
		epsilon = 40
		for(i in 1:10) {
    		up = good_dots$y[i] + good_dots$sd[i]
    		low = good_dots$y[i] - good_dots$sd[i]
    		segments(good_dots$x[i],low , good_dots$x[i], up)
    		segments(good_dots$x[i]-epsilon, up , good_dots$x[i]+epsilon, up)
    		segments(good_dots$x[i]-epsilon, low , good_dots$x[i]+epsilon, low)
		}

Q4
	fast_food = regexpr(" Fast Food", yelp_dat[, 'categories'], ignore.case = TRUE) != -1
	boxplot(yelp_dat[, 'stars']~fast_food, main = "Fast food vs. stars", xlab = "Fast food Category", ylab = "Stars")

	lv_flag = regexpr(" Las Vegas", yelp_dat[, 'city'], ignore.case = TRUE) != -1
	boxplot(yelp_dat[, 'review_count']~lv_flag, main = "Las Vegas vs. review count", xlab = "Las Vegas", ylab = "Review Count")







		
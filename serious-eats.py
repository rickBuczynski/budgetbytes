import urllib3
from bs4 import BeautifulSoup # To get everything
import math
import sys

http = urllib3.PoolManager()

dairy_words = ['brie', 'feta', 'gouda', 'provolone', 'mozzarella', 'parmesan', 'cheddar', 'butter', 'cream', 'butter', 'milk', 'cheese', 'yogurt']

def get_soup_url(url):
	return BeautifulSoup(http.request('GET', url).data, "html.parser").body

def get_soup_file(file):
	file = open(file, 'r', encoding=sys.getdefaultencoding())
	return BeautifulSoup(file.read(), "html.parser").body

# http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
def ci_lower_bound(pos, n):
	if n == 0:
		return 0
	z = 1.96 # hard-code a value here for z. (Use 1.96 for a confidence level of 0.95.)
	phat = 1.0*pos/n
	return (phat + z*z/(2*n) - z * math.sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)

# http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
def ci_lower_bound_5_star(average_rating, rating_count):
    return 100 * ci_lower_bound( int((average_rating - 1) / 4 * rating_count), rating_count)
	
print('name, url, comments, stars, lower bound, is_dairy')
page = get_soup_file('seriouseats-recipes-topics-mains')
#print(page)
recipeTags = page.findAll('h4', attrs={'class' : 'title'})
for recipeTag in recipeTags:
	recipe_name = recipeTag.contents[0].contents[0].replace(',','')
	recipe_url = recipeTag.contents[0].get("href")
	comment_count_data = get_soup_url(recipe_url).findAll('span', attrs={'class' : 'comment-number'})
	stars_rating_data = get_soup_url(recipe_url).findAll('span', attrs={'class' : 'info rating-value'})
	
	comment_count = comment_count_data[0].contents[0] if len(comment_count_data) > 0 else ""
	stars_rating = stars_rating_data[0].contents[0] if len(stars_rating_data) > 0 else ""
	
	lower_bound = ""
	if (len(comment_count_data) > 0) & (len(stars_rating_data) > 0):
		lower_bound = ci_lower_bound_5_star(float(stars_rating), int(comment_count))

	print("{}, {}, {}, {}, {}".format(recipe_name, recipe_url, comment_count, stars_rating, lower_bound))

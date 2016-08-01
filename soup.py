import urllib3
from bs4 import BeautifulSoup # To get everything
import math

http = urllib3.PoolManager()

def get_soup(url):
	return BeautifulSoup(http.request('GET', url).data, "html.parser").body

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
	
print('name, url, ratings, avg, lower bound')

for page in range(1, 11):
	page_of_recipes = get_soup('http://www.budgetbytes.com/category/recipes/page/{}/'.format(page))
	recipeTags = page_of_recipes.findAll('a', attrs={'class' : 'entry-image-link'})

	for recipeTag in recipeTags:
		single_recipe_page = get_soup(recipeTag['href'])
		average_rating_data = single_recipe_page.findAll('span', attrs={'class' : 'average'})
		rating_count_data = single_recipe_page.findAll('span', attrs={'class' : 'count'})
		
		if len(average_rating_data) == 1 & len(rating_count_data) == 1:
			average_rating = float(average_rating_data[0].contents[0])
			rating_count = int(rating_count_data[0].contents[0])
			
			url = recipeTag['href']
			name = url.split('/')[-2].replace('-', ' ')
			lower_bound = ci_lower_bound_5_star(average_rating, rating_count)

			print("{}, {}, {}, {}, {}".format(name, url, rating_count, average_rating, lower_bound))


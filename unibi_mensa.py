from bs4 import BeautifulSoup
import urllib
import re
import collections

MENSA_LINK_BASE = "http://www.studentenwerkbielefeld.de/index.php?id=61&tx_studentenwerk_pi1%5Bweek%5D="
ERROR = "There's been an error.."

def GetURL(week=0):
    if week <= 1 and week >= 0:
        mensa_url = "".join([MENSA_LINK_BASE, str(week)])
        return mensa_url
    else:
        return ERROR

def Crawler(mensa_url):
    content = urllib.urlopen(mensa_url).read()
    content_soup = BeautifulSoup(content)

    for tag in content_soup.find_all("td", class_="price"):
        tag.decompose()

    [tag.decompose() for tag in content_soup(['th', 'sup', 'img', 'b', 'br'])]

    dayblocks = [dayblock.prettify() for dayblock in content_soup.find_all("div", class_="day-block")]

    db = BeautifulSoup("".join(dayblocks))
    days = db.find_all("div", class_="day-block")

    meal_dict = {}
    meal_dict = collections.OrderedDict(sorted(meal_dict.items()))

    for day in days:
        date = [day.a.getText().strip().split(",")[0], day.a.getText().strip().split(",")[1]]
        try:
            meal_main = day.find_all("tr")[0]
            meal_vegt = day.find_all("tr")[1]
            meal_soup = day.find_all("tr")[3]

            side_courses_main = [sc.split('\n')[0].strip() for sc in meal_main.find_all("p")[1].getText().strip().split(",")]
            side_courses_vegt = [sc.split('\n')[0].strip() for sc in meal_vegt.find_all("p")[1].getText().strip().split(",")]
            side_courses = side_courses_main + side_courses_vegt
            side_courses = filter(None, side_courses)
            side_courses = [sc for sc in side_courses if len(sc)>1 and sc != 'oder']

            meal_dict[date[0]] = [date[1],
                                  meal_main.getText().split(' Es')[0],
                                  meal_vegt.getText().split(' Es')[0],
                                  '<br />Dazu: '.join(meal_soup.getText().split(' Dazu gibt es:')),
                                  ',<br />'.join(list(set(side_courses)))]
        except IndexError:
            meal_dict[date[0]] = [date[1],
                                  "Feiertag",
                                  "",
                                  "",
                                  ""]

    return meal_dict

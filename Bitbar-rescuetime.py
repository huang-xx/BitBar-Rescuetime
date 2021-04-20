#!/Users/huangyingfan3/anaconda3/bin/python
# coding=utf-8
# <bitbar.title>RescueTime Productive Time</bitbar.title>
# <bitbar.version>v2.0</bitbar.version>
# <bitbar.author>Jason Benn</bitbar.author>
# <bitbar.author.github>JasonBenn</bitbar.author.github>
# <bitbar.desc>Show your RescueTime very productive time & pulse in the status bar</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
#
# To install, you will want to generate an API key for rescue time and then store the
# key in ~/Library/RescueTime.com/api.key
# https://www.rescuetime.com/anapi/manage
import datetime
import os
import json
import urllib
from urllib.request import urlopen
import math
import time

# leetcode-cn progress part
import requests

url = "https://leetcode-cn.com/graphql/"
payload = "{\"operationName\":\"userQuestionProgress\",\"variables\":{\"userSlug\":\"huang-xx-m\"},\"query\":\"query userQuestionProgress($userSlug: String!) {\\n  userProfileUserQuestionProgress(userSlug: $userSlug) {\\n    numAcceptedQuestions {\\n      difficulty\\n      count\\n      __typename\\n    }\\n    numFailedQuestions {\\n      difficulty\\n      count\\n      __typename\\n    }\\n    numUntouchedQuestions {\\n      difficulty\\n      count\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}\n"
headers = {
    'content-type': "application/json",
    'referer': "https://leetcode-cn.com/progress/",
    'origin': "https://leetcode-cn.com",
    'cache-control': "no-cache",
    'postman-token': "b69fb818-d135-ceed-ae70-c171ff0612da"
    }
response = requests.request("POST", url, data=payload, headers=headers)
response_dict = json.loads(response.text)['data']
user_progress = response_dict['userProfileUserQuestionProgress']
ac_count = sum([d['count'] for d in user_progress['numAcceptedQuestions']])
filed_count = sum(d['count'] for d in  user_progress['numFailedQuestions'])
untouched_count = sum(d['count'] for d in user_progress['numUntouchedQuestions'])
all_problem_count = ac_count + filed_count + untouched_count
ac_ratio = round(ac_count / all_problem_count, 4)

'''leetcode progress part
import requests
import json
url = "https://leetcode.com/graphql"
payload = "{\"operationName\":\"getUserProfile\",\"variables\":{\"username\":\"xx_huang\"},\"query\":\"query getUserProfile($username: String!) {\\n  allQuestionsCount {\\n    difficulty\\n    count\\n    __typename\\n  }\\n  matchedUser(username: $username) {\\n    username\\n    socialAccounts\\n    githubUrl\\n    contributions {\\n      points\\n      questionCount\\n      testcaseCount\\n      __typename\\n    }\\n    profile {\\n      realName\\n      websites\\n      countryName\\n      skillTags\\n      company\\n      school\\n      starRating\\n      aboutMe\\n      userAvatar\\n      reputation\\n      ranking\\n      __typename\\n    }\\n    submissionCalendar\\n    submitStats {\\n      acSubmissionNum {\\n        difficulty\\n        count\\n        submissions\\n        __typename\\n      }\\n      totalSubmissionNum {\\n        difficulty\\n        count\\n        submissions\\n        __typename\\n      }\\n      __typename\\n    }\\n    badges {\\n      id\\n      displayName\\n      icon\\n      creationDate\\n      __typename\\n    }\\n    upcomingBadges {\\n      name\\n      icon\\n      __typename\\n    }\\n    activeBadge {\\n      id\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}\n"
headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "9dda656b-af61-49af-20f9-70543ddbea1f"
    }
response = requests.request("POST", url, data=payload, headers=headers)
response_dict = json.loads(response.text)['data']
all_problem_count = max([d['count'] for d in response_dict['allQuestionsCount']])
all_ac_count = max([d['count'] for d in response_dict['matchedUser']['submitStats']['acSubmissionNum']])
ac_ratio = all_ac_count / all_problem_count
print(f'count: {all_ac_count} ratio: {ac_ratio:.3f}')
'''



# RescueTime Part
def get(url, params):
    """Simple function to mimic the signature of requests.get"""
    params = urllib.parse.urlencode(params)
    result = urlopen(url + "?" + params).read()
    return json.loads(result)


def h_to_t(hours_float):
    hours = int(hours_float)
    mins = int(hours_float % 1 * 60)
    return "{}:{:02d}".format(hours, mins)


def getCurrHour():
    localtime = time.asctime(time.localtime(time.time()))
    return int(localtime.split()[-2].split(":")[0])


def getColorFromScore(score):
    # return "red" if score < 80 else "black"
    # return "red" if score < 80 else "white"
    return 'red'


def getTickOrCross(score):
    return "✅" if score >= 80 else "❌"


MAPPING = {
    2: "Very Productive",
    1: "Productive",
    0: "Neutral",
    -1: "Distracting",
    -2: "Very Distracting",
}

API_KEY = os.path.expanduser("~/Library/RescueTime.com/api.key")
if not os.path.exists(API_KEY):
    print("X")
    print("---")
    print("Missing API Key")
    exit()

key = open(API_KEY).read().strip()
date = datetime.date.today().strftime("%Y-%m-%d")

data = get(
    "https://www.rescuetime.com/anapi/data",
    params={
        "format": "json",
        "key": key,
        "resolution_time": "day",
        "restrict_begin": date,
        "restrict_end": date,
        "restrict_kind": "productivity",
    },
)

data_detail = get(
    "https://www.rescuetime.com/anapi/data",
    params={
        "format": "json",
        "key": key,
        "resolution_time": "day",
        "restrict_begin": date,
        "restrict_end": date,
        "restrict_kind": "activity",
    },
)

coding_time_today = (
    float(
        sum(
            x[1]
            for x in data_detail["rows"]
            if x[3] in ["leetcode-cn.com", "leetcode.com", "leetcode"]
        )
    )
    / 60
    / 60
)


pulse = get(
    "https://www.rescuetime.com/anapi/current_productivity_pulse.json",
    params={"key": key},
)


activities = data["rows"]
time_today = float(sum([x[1] for x in activities])) / 60 / 60
vp_time_today = float(sum([x[1] for x in activities if x[3] == 2])) / 60 / 60
p_time_today = float(sum([x[1] for x in activities if x[3] == 1])) / 60 / 60
n_time_today = float(sum([x[1] for x in activities if x[3] == 0])) / 60 / 60
d_time_today = float(sum([x[1] for x in activities if x[3] == -1])) / 60 / 60
vd_time_today = float(sum([x[1] for x in activities if x[3] == -2])) / 60 / 60

score = round(
    (
        1 * vp_time_today
        + 0.75 * p_time_today
        + 0.5 * n_time_today
        + 0.25 * d_time_today
        + 0 * vd_time_today
    )
    / time_today
    * 100,
    2,
)

# pulse_color = pulse['color']
pulse_color = getColorFromScore(score)
print(
    "🎯 {}% ({} of {})  🚀 {}: {} | color={}".format(
        score,
        h_to_t(vp_time_today),
        h_to_t(time_today),
        ac_count,
        ac_ratio,
        pulse_color,
    )
)

print("---")

# Print summaries for last 7 days
summary = get(
    "https://www.rescuetime.com/anapi/daily_summary_feed.json", params={"key": key}
)
last_7_days = summary[:7]
last_7_as_days_of_week = [
    datetime.datetime.strptime(x["date"], "%Y-%m-%d").weekday() for x in last_7_days
]
monday_index = last_7_as_days_of_week.index(0)
this_week_daily_summaries = last_7_days[: monday_index + 1]

week_vp_time = vp_time_today
week_time = time_today

for x in this_week_daily_summaries:
    day = datetime.datetime.strptime(x["date"], "%Y-%m-%d").strftime("%A")
    print(
        "{}  {}: {}%  Dev: [{}]| color={}".format(
            getTickOrCross(x["productivity_pulse"]),
            day,
            x["productivity_pulse"],
            h_to_t(x["software_development_hours"]),
            getColorFromScore(x["productivity_pulse"]),
        )
    )
    day_time = (
        x["all_productive_hours"] + x["neutral_hours"] + x["all_distracting_hours"]
    )
    day_vp_time = x["very_productive_hours"]
    print(
        "{} of {} ({}%)".format(
            h_to_t(day_vp_time), h_to_t(day_time), x["very_productive_percentage"]
        )
    )
    print("---")
    week_vp_time += day_vp_time
    week_time += day_time


print("Week Summary: ({} of {})".format(h_to_t(week_vp_time), h_to_t(week_time)))

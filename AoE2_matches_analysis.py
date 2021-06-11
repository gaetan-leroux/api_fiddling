import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

# Get mapping codification to understand variables returned by the API
strings_request = requests.get('https://aoe2.net/api/strings?game=aoe2de&language=en')
strings_dict = json.loads(strings_request.content.decode('UTF-8'))

# Get data about the last X matches since a specific time
nb_match = 100
start_time = datetime(2021, 6, 1)
match_request = requests.get(
    f'https://aoe2.net/api/matches?game=aoe2de&count={nb_match}&since={int(start_time.timestamp())}')
match_dict = json.loads(match_request.content.decode('utf-8'))

# Define specific variables to keep, relative to match and player, respectively
match_var = ['match_id', 'leaderboard_id', 'map_type', 'started', 'finished', 'players']
player_var = ['profile_id', 'rating', 'civ', 'won']

# Turn dict into dataframe (loop requested because of dict structure) and select match variables
data_match = pd.DataFrame()
for i in range(match_dict.__len__()):
    data_match = data_match.append(pd.DataFrame.from_dict(match_dict[i])[match_var])

# Extract nested information in 'players' variable
data_match[['profile_id', 'rating', 'civ', 'won']] = data_match['players'].apply(
    lambda x: pd.Series(x[k] for k in player_var))
data_match = data_match.drop('players', axis=1)

# Use dictionaries to map id of some variables to their meaning
map_type_dict = {index_dict['id']: index_dict['string'] for _, index_dict in enumerate(strings_dict['map_type'])}
data_match['map_type'] = data_match['map_type'].map(map_type_dict)
leaderboard_id_dict = {index_dict['id']: index_dict['string'] for _, index_dict in
                       enumerate(strings_dict['leaderboard'])}
data_match['leaderboard_id'] = data_match['leaderboard_id'].map(leaderboard_id_dict)
civ_dict = {index_dict['id']: index_dict['string'] for _, index_dict in enumerate(strings_dict['civ'])}
data_match['civ'] = data_match['civ'].map(civ_dict)

# Compute match duration
data_match['duration'] = (data_match['finished'] - data_match['started']) / 60

# Distribution of ELO rating
sns.displot(data_match['rating'], kde=True)
plt.title(f'Density plot of ELO ratings for the last {nb_match} matches')
plt.xlabel('ELO rating')
plt.ylabel('Count')

# Distribution of civilization choices
civ_plot = sns.countplot(data_match['civ'], order=data_match['civ'].sort_values().unique())
civ_plot.set_xticklabels(labels=civ_plot.get_xticklabels(), rotation=30)
plt.title(f'Density plot of civilization choices for the last {nb_match} matches')
plt.xlabel('Civilization')
plt.ylabel('Count')

# Distribution of maps
map_plot = sns.countplot(data_match['map_type'], order=data_match['map_type'].sort_values().unique())
map_plot.set_xticklabels(labels=map_plot.get_xticklabels(), rotation=30)
plt.title(f'Density plot of maps for the last {nb_match} matches')
plt.xlabel('Maps')
plt.ylabel('Count')

# Distribution of duration
sns.displot(data_match['duration'], kde=True)
plt.title(f'Density plot of matches duration for the last {nb_match} matches')
plt.xlabel('Match duration (minutes)')
plt.ylabel('Count')

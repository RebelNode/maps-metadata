# Generates maplists for https://github.com/beyond-all-reason/spads_config_bar/blob/main/etc/mapLists.conf . This controls the !nextmap command in spads.

import json
import math
from collections import defaultdict

teamsizes = ['2v2','3v3','4v4','5v5','6v6','7v7','8v8','ffa3','ffa4','ffa5','ffa6','ffa7','ffa8','ffa9','ffa10','ffa11','ffa12','ffa13','ffa14','ffa15','ffa16','2v2v2','2v2v2v2','2v2v2v2v2','2v2v2v2v2v2','2v2v2v2v2v2v2','2v2v2v2v2v2v2v2','3v3v3','3v3v3v3','3v3v3v3v3','4v4v4','4v4v4v4','5v5v5']

def get_data(input_file):
    with open(input_file) as f:
        contents = json.load(f)
    
    teamsize_dict = {}
    certified_maps = []
    uncertified_maps = []
    maps_1v1 = []
    map_lists = defaultdict(set)

    for i in teamsizes:
        teamsize_dict[i] = []

    for map in contents.values():
        for l in map["mapLists"]:
            map_lists[l].add(map["springName"])
        if map["startPosActive"]:
            map_lists["withstartpos"].add(map["springName"])

        if not map["inPool"] or "special" in map and map["special"] in ['Metal', 'No Metal']:
            continue
        is_team = False
        mapname = ''
        player_count = 0


        mapname = map["springName"]
        is_team = "team" in map["gameType"]

        if "playerCount" in map:
            player_count = map["playerCount"]
        #32 player ffa or other such sillyness not supported in !nextmap
        if player_count > 16:
            player_count = 16
        if player_count < 2:
            player_count = 2
        if "minPlayerCount" in map:
            min_player_count = map["minPlayerCount"]

        if "startboxesSet" in map:
            for startboxes_info in map["startboxesSet"].values():
                if "maxPlayersPerStartbox" in startboxes_info:
                    team_count = len(startboxes_info["startboxes"])
                    if team_count == 1:
                        # Let's ignore the case when there is only 1 team. Maybe it should be
                        # just illegal in the rowy, but for now, there are some maps like that.
                        continue
                    max_players_per_startbox = startboxes_info["maxPlayersPerStartbox"]

                    # add teamgame maps to teamsize_dict
                    if team_count*max_players_per_startbox <= 16 and is_team:
                        for x in range(2,max_players_per_startbox+1): 
                            if "minPlayerCount" in map and team_count:
                                if x >= min_player_count/team_count:
                                    teamsize_dict['v'.join([str(x)] * team_count)].append(mapname)
                            elif x >= math.ceil(max_players_per_startbox*0.6):
                                teamsize_dict['v'.join([str(x)] * team_count)].append(mapname)

                # if a map didn't have "maxPlayersPerStartbox" set for its startboxes, but it's a teamgame map with startboxes for 2 teams, we'll use playerCount instead:
                if not "maxPlayersPerStartbox" in startboxes_info and player_count and is_team:
                    team_count = len(startboxes_info["startboxes"])
                    if team_count == 2 and player_count >=4:
                        for x in range(2,math.floor(player_count/2)+1): 
                            if "minPlayerCount" in map:
                                if x >= min_player_count:
                                    teamsize_dict['v'.join([str(x)] * team_count)].append(mapname)
                            elif x >= math.ceil(player_count/4):
                                teamsize_dict['v'.join([str(x)] * team_count)].append(mapname)

        # add ffa maps to teamsize_dict
        if "ffa" in map["gameType"]:
            for x in range(3,17):
                if "minPlayerCount" in map:
                    if x <= player_count and x >= min_player_count:
                        teamsize_dict['ffa' + str(x)].append(mapname)
                elif x <= player_count and x >= math.floor(player_count/2):
                    teamsize_dict['ffa' + str(x)].append(mapname)

        # add maps to certified and uncertified lists
        if map["certified"]:
            certified_maps.append(mapname)
        else:
            uncertified_maps.append(mapname)
        
        # add maps to 1v1 list
        if "1v1" in map["gameType"]:
            maps_1v1.append(mapname)

    # make the lists more human-readable
    for maplist in teamsize_dict.values():
        maplist.sort()
    
    certified_maps.sort()
    uncertified_maps.sort()
    maps_1v1.sort()

    # if combined_dict has empty lists then add ".*" (meaning all maps) to that list
    for i in teamsize_dict:
        if len(teamsize_dict[i]) == 0:
            teamsize_dict[i].append('.*')
    
    return teamsize_dict, certified_maps, uncertified_maps, maps_1v1, map_lists

def get_output_string(teamsize_dict, certified_maps, uncertified_maps, maps_1v1, map_lists):
    nl = '\n'
    output_string = f"""# This file was automatically generated by https://github.com/beyond-all-reason/maps-metadata/tree/main/scripts/py/gen_nextmap_maplists.py using data from rowy.
# Next update from rowy will overwrite this file so do not manually edit this file.
# If you want to make updates to this see https://github.com/beyond-all-reason/maps-metadata/wiki/Adding-a-created-map-to-the-game.
# A map needs properly configured playercount, startboxes and maxPlayersPerStartbox in https://rowy.beyondallreason.dev/table/maps to appear here.
# For example a 2v2v2v2 map needs a startbox configuration with 4 startboxes and maxPlayersPerStartbox >= 2.
[all]
.*

[certified]
{nl.join(certified_maps)}

[uncertified]
{nl.join(uncertified_maps)}

[small]
.*

[medium]
.*

[large]
.*

[extraLarge]
.*

[misc]
.*

[1v1]
{nl.join(maps_1v1)}

"""
    
    for i in teamsize_dict:
        output_string = output_string + '[' + i + ']\n'
        output_string += '\n'.join(teamsize_dict[i])
        output_string = output_string + '\n\n'

    output_string += '\n# Custom maplists\n\n'
    for l in sorted(map_lists.keys()):
        output_string += f"[{l}]\n"
        output_string += '\n'.join(sorted(map_lists[l]))
        output_string += '\n\n'

    return output_string

def process(input_file,mapLists_conf,custom_map_lists_json):
    teamsize_dict, certified_maps, uncertified_maps, maps_1v1, map_lists = get_data(input_file)
    output = get_output_string(teamsize_dict, certified_maps, uncertified_maps, maps_1v1, map_lists)
    with open(mapLists_conf, "w") as f:
        f.write(output)
    with open(custom_map_lists_json, "w") as f:
        f.write(json.dumps(sorted(map_lists.keys()), indent=4))

if __name__ == '__main__':
    input_file = './gen/map_list.validated.json'
    mapLists_conf = './gen/mapLists.conf'
    custom_map_lists_json = './gen/custom_map_lists.json'
    process(input_file, mapLists_conf, custom_map_lists_json)

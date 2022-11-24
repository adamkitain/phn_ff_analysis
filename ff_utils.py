YEARS = range(2012, 2023)
import pandas as pd

def owner_clean(owner):
    if owner == 'Zachary Havanec':
        return "Zack Havanec"
    if owner == 'Alexander Han':
        return 'Alex Han'
    if owner == 'Arthur Cheokas':
        return 'Athan Cheokas'
    return owner

def _get_matchup_dict(matchup, period):
    whoa = matchup.data['winner']
    lhoa = 'HOME' if whoa == 'HOME' else 'AWAY'
    if whoa == 'AWAY':
        winner = matchup.away_team
        loser = matchup.home_team
        winning_score = matchup.away_score
        losing_score = matchup.home_score
    elif whoa == 'HOME':
        winner = matchup.home_team
        loser = matchup.away_team
        winning_score = matchup.home_score
        losing_score = matchup.away_score
    elif whoa == 'UNDECIDED':
        winner = matchup.home_team
        loser = matchup.away_team
        winning_score = matchup.home_score
        losing_score = matchup.away_score
    return dict(
        period=matchup.data['matchupPeriodId'],
        home_team=owner_clean(matchup.home_team.owner),
        away_team=owner_clean(matchup.away_team.owner if matchup.away_team else ""),
        winner=owner_clean(winner.owner),
        loser=owner_clean(loser.owner if loser else ""),
        winning_score=winning_score,
        losing_score=losing_score,
        winning_scoring_breakdown=matchup.data[whoa.lower()]['pointsByScoringPeriod'],
        losing_scoring_breakdown=matchup.data[lhoa.lower()]['pointsByScoringPeriod'],
        is_playoff=matchup.is_playoff,
        matchup_type=matchup.matchup_type,
        point_differential=winning_score-losing_score
    )

def _get_game_dict(matchup, hoa="HOME"):
    if hoa == 'AWAY':
        team = matchup.away_team
        opp = matchup.home_team
        team_score = matchup.away_score
        opp_score = matchup.home_score
    elif hoa == 'HOME':
        team = matchup.home_team
        opp = matchup.away_team
        team_score = matchup.home_score
        opp_score = matchup.away_score
    else:
        raise Exception("can only be home or away team")
    if team == 0:
        return
    whoa = matchup.data['winner']
    win = 0
    loss = 0
    if whoa == 'UNDECIDED':
        result = 'NO CONTEST'
    elif whoa == hoa:
        win = 1
        result = 'WIN'
    else:
        loss = 1
        result = 'LOSS'
        
    return dict(
        period=matchup.data['matchupPeriodId'],
        team=owner_clean(team.owner),
        team_name=team.team_name,
        opponent=owner_clean(opp.owner if opp else ""),
        opponent_name=opp.team_name if opp else "",
        team_score=team_score,
        opponent_score=opp_score,
        differential=abs(team_score-opp_score),
        win=win,
        loss=loss,
        result=result,
#         winner=winner.owner,
#         loser=loser.owner if loser else "",
#         winning_score=winning_score,
#         losing_score=losing_score,
#         winning_scoring_breakdown=matchup.data[whoa.lower()]['pointsByScoringPeriod'],
#         losing_scoring_breakdown=matchup.data[lhoa.lower()]['pointsByScoringPeriod'],
        is_playoff=matchup.is_playoff,
        matchup_type=matchup.matchup_type,
#         point_differential=winning_score-losing_score
    )


def _get_matchups(years=None):
    matchups_dicts = []
    if years is None:
        years = range(2012,2023)
    for year in years:
        league = league_map[year]
        for i in range(league.firstScoringPeriod, league.finalScoringPeriod):
            matchups = league.scoreboard(week=i)
            for matchup in matchups:
                matchup_dict = _get_matchup_dict(matchup)
                matchup_dict['year'] = year
                matchups_dicts.append(matchup_dict)
    return matchups_dicts


def _get_game_dicts(years=None):
    game_dicts = []
    if years is None:
        years = range(2012,2023)
    for year in years:
        league = league_map[year]
        for i in range(league.firstScoringPeriod, league.finalScoringPeriod):
            matchups = league.scoreboard(week=i)
            for matchup in matchups:
                for hoa in ["HOME", "AWAY"]:
                    game_dict = _get_game_dict(matchup, hoa)
                    if game_dict:
                        game_dict['year'] = year
                        game_dicts.append(game_dict)
    return game_dicts

def save_game_data_to_csv(years=None):
    if years is None:
        years = YEARS
    for yr in years:
        gd = _get_game_dicts([yr])
        df = pd.DataFrame(gd)
        df.to_csv(f"all_games_{yr}.csv", header=True, index=False)

def load_game_data_from_csv(years=None):
    year_dfs = []
    if years is None:
        years = YEARS
    for yr in years:
        year_dfs.append(pd.read_csv(f"all_games_{yr}.csv"))
    return pd.concat(year_dfs)
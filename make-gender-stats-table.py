# This script collects the reviews, meta-reviews, and final decisions of all
# MIDL papers and partitions them by gender if gender is available in the OpenReview
# profile.

import openreview
import pandas as pd
from tqdm import tqdm

client = openreview.Client(
    baseurl="https://api.openreview.net",
    username="",
    password="",
)
all_papers = client.get_notes(
    invitation="MIDL.io/2022/Conference/-/Submission", details="replies"
)


def get_score_from_description(description):
    if type(description) == str and description[0] in ["1", "2", "3", "4", "5"]:
        return int(description[0])
    else:
        # do nothing if description doesn't start with a numeric string
        return description


def get_gender_from_id(id):
    try:
        profile = client.get_profile(id)
        gender = profile.content["gender"] if "gender" in profile.content else "unknown"
    except:
        print(f"First author profile for {first_author_id} not found. Filling in blank")
        gender = "unknown"
    return gender


review_info_list = []
for paper in tqdm(all_papers):

    authorids = paper.content["authorids"]
    paperid = paper.id
    paper_title = paper.content["title"]
    first_author_id = authorids[0]
    last_author_id = authorids[-1]

    first_author_gender = get_gender_from_id(first_author_id)
    last_author_gender = get_gender_from_id(last_author_id)

    for reply in paper.details["replies"]:
        row = {
            "first_author_gender": first_author_gender,
            "last_author_gender": last_author_gender,
            "paperid": paperid,
            "paper_title": paper_title,
        }
        if "preliminary_rating" in reply["content"]:
            # This is a review
            row["preliminary_rating"] = get_score_from_description(
                reply["content"]["preliminary_rating"]
            )
            if "final_rating_after_the_rebuttal" in reply["content"]:
                row["final_rating_after_the_rebuttal"] = get_score_from_description(
                    reply["content"]["final_rating_after_the_rebuttal"]
                )
            else:
                row["final_rating_after_the_rebuttal"] = row["preliminary_rating"]
        elif "recommendation" in reply["content"]:
            # This is a meta-review
            row["meta_rating"] = reply["content"]["recommendation"]
        elif "decision" in reply["content"]:
            # This is a final decision
            row["final_decision"] = reply["content"]["decision"]
        else:
            # Some other comment we don't care about
            continue

        row["signature"] = reply["signatures"][0]
        review_info_list.append(row)

review_info = pd.DataFrame(review_info_list)
review_info.to_csv("gender-stats-table.csv")

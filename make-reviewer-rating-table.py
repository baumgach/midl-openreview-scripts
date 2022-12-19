# This script aggregates the reviewer ratings for all reviewers. That is
# the ratings the reviewers received from the ACs for each of their
# reviews. The output of this script can be used to determine best
# reviewer awards.

import openreview
import pandas as pd
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

logging.info("Open connection")
client = openreview.Client(
    baseurl="https://api.openreview.net",
    username="",
    password="",
)

logging.info("Get all replies")
all_papers = client.get_all_notes(
    invitation="MIDL.io/2022/Conference/-/Submission", details="replies"
)


def get_identiy_from_invitatiton(invitation):
    rid = "/".join(invitation.split("/")[:5])
    group = client.get_group(rid)
    return group.members[0]


logging.info("Parse all notes")
review_list = []
reviewer_counter = {}
reviewer_fields = [
    "summary",
    "justification_of_the_final_rating",
    "confidence",
    "recommendation",
    "special_issue",
    "preliminary_rating",
    "final_rating_after_the_rebuttal",
]

reviewers = {}
max_num_scores = 0

all_scores = []

for paper in tqdm(all_papers):
    replies = paper.details["replies"]
    for reply in replies:
        if reply["invitation"].endswith("Review_Rating"):
            reviewer_name = get_identiy_from_invitatiton(reply["invitation"])
            review_score = int(reply["content"]["review_quality"])
            if not reviewer_name in reviewers:
                reviewers[reviewer_name] = {}
                reviewers[reviewer_name]["num_scores"] = 1
                reviewers[reviewer_name]["score_1"] = review_score
                reviewers[reviewer_name]["score_average"] = review_score
            else:
                reviewers[reviewer_name]["num_scores"] += 1
                score_key = f"score_{reviewers[reviewer_name]['num_scores']}"
                reviewers[reviewer_name][score_key] = review_score
                reviewers[reviewer_name]["score_average"] += review_score
                max_num_scores = max(
                    max_num_scores, reviewers[reviewer_name]["num_scores"]
                )
            all_scores.append(review_score)

for reviewer in reviewers.keys():
    reviewers[reviewer]["score_average"] /= reviewers[reviewer]["num_scores"]

logging.info("Convert data to pandas and write to csv")
column_order = [f"score_{s}" for s in range(1, max_num_scores + 1)] + [
    "num_scores",
    "score_average",
]
reviews = pd.DataFrame.from_dict(reviewers, orient="index")
reviews = reviews[column_order]
reviews.to_csv("reviewer-rating-table.csv")

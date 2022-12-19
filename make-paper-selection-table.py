# This script collects the reviews, meta-reviews, and final decisions of all
# MIDL papers and partitions them by gender if gender is available in the OpenReview
# profile.

import openreview
import pandas as pd
from tqdm import tqdm
import logging

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


reviewer_fields = [
    "summary",
    "justification_of_the_final_rating",
    "confidence",
    "recommendation",
    "special_issue",
    "preliminary_rating",
    "final_rating_after_the_rebuttal",
]

ac_fields = [
    "recommendation",
    "confidence",
    "metareview",
]

paper_dict = {}
for paper in tqdm(all_papers):

    # General paper infos
    papernumber = paper.number
    # paperid = paper.id  # not currently used, but may be useful in the future
    title = paper.content["title"]
    authors = paper.content["authors"]

    if papernumber not in paper_dict:
        paper_dict[papernumber] = {"title": title, "authors": authors, "num_reviews": 0}

    for reply in paper.details["replies"]:

        if "preliminary_rating" in reply["content"]:
            # This is a review

            paper_dict[papernumber]["num_reviews"] += 1  # increase review counter

            reviewer_fields_out = [
                f"R{paper_dict[papernumber]['num_reviews']}_{s}"
                for s in reviewer_fields
            ]

            for fo, fi in zip(reviewer_fields_out, reviewer_fields):
                data = reply["content"][fi] if fi in reply["content"] else None
                paper_dict[papernumber][fo] = get_score_from_description(data)

            # If no final rating insert preliminary rating into the field
            if "final_rating_after_the_rebuttal" not in reply["content"]:
                paper_dict[papernumber][
                    f"R{paper_dict[papernumber]['num_reviews']}_final_rating_after_the_rebuttal"
                ] = (
                    get_score_from_description(reply["content"]["preliminary_rating"])
                    + 0.001
                )  # 0.01 so we can identify these cases in the spreadsheet

        elif "recommendation" in reply["content"]:
            # This is a meta-review

            ac_fields_out = [f"MR_{s}" for s in ac_fields]
            for fo, fi in zip(ac_fields_out, ac_fields):
                data = reply["content"][fi] if fi in reply["content"] else None
                paper_dict[papernumber][fo] = get_score_from_description(data)

        else:
            # Some other comment we don't care about
            continue


logging.info("Convert data to pandas and write to csv")
column_order = (
    ["title", "authors"]
    + [f"R{rev+1}_{s}" for s in reviewer_fields for rev in range(6)]
    + ac_fields_out
)
reviews = pd.DataFrame.from_dict(paper_dict, orient="index")
reviews = reviews[column_order]
reviews.to_csv("paper-selection-table.csv")

import csv
import json

import pandas as pd
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import paraphrase_mining

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("../resources/mapping.json") as mapping_file:
    mapping_data = json.load(mapping_file)

del mapping_data["_comment"]

data = {
    "identifier": [],
    "description": [],
    "description_ner": [],
    "dexms_entity": []
}

for key, mapping in mapping_data.items():
    for element in mapping:
        data["identifier"].append(element["identifier"])
        data["description"].append(element["description"])
        data["description_ner"].append(element["description_ner"])
        data["dexms_entity"].append(key)

df = pd.DataFrame(data=data)
descriptions = df["description"].tolist()
descriptions_ner = df["description_ner"].tolist()

paraphrases = paraphrase_mining(model, descriptions)
paraphrases_ner = paraphrase_mining(model, descriptions_ner)

paraphrase_scores = [{} for i in range(len(descriptions))]

for paraphrase in paraphrases:
    score, i, j = paraphrase

    paraphrase_scores[i][j] = score
    paraphrase_scores[j][i] = score

paraphrase_ner_scores = [{} for i in range(len(descriptions_ner))]

for paraphrase in paraphrases_ner:
    score, i, j = paraphrase

    paraphrase_ner_scores[i][j] = score
    paraphrase_ner_scores[j][i] = score

with open('../resources/similarity_results.csv', 'w', newline='', encoding='utf8') as f:
    dict_writer = csv.DictWriter(f, fieldnames=["identifier_0", "identifier_1", "sentence_0", "sentence_1", "dexms_0", "dexms_1", "score"])
    dict_writer.writeheader()

    for i in range(len(paraphrase_scores)):
        for j in range(i+1, len(paraphrase_scores)):
            row_as_dict = {
                "identifier_0": df.iloc[i]["identifier"],
                "identifier_1": df.iloc[j]["identifier"],
                "sentence_0": df.iloc[i]["description"],
                "sentence_1": df.iloc[j]["description"],
                "dexms_0": df.iloc[i]["dexms_entity"],
                "dexms_1": df.iloc[j]["dexms_entity"],
                "score": paraphrase_scores[i][j]
            }

            dict_writer.writerow(row_as_dict)

with open('../resources/similarity_results_ner.csv', 'w', newline='', encoding='utf8') as f:
    dict_writer = csv.DictWriter(f, fieldnames=["identifier_0", "identifier_1", "sentence_0", "sentence_1", "dexms_0",
                                                "dexms_1", "score"])
    dict_writer.writeheader()

    for i in range(len(paraphrase_ner_scores)):
        for j in range(i+1, len(paraphrase_ner_scores)):
            row_as_dict = {
                "identifier_0": df.iloc[i]["identifier"],
                "identifier_1": df.iloc[j]["identifier"],
                "sentence_0": df.iloc[i]["description_ner"],
                "sentence_1": df.iloc[j]["description_ner"],
                "dexms_0": df.iloc[i]["dexms_entity"],
                "dexms_1": df.iloc[j]["dexms_entity"],
                "score": paraphrase_ner_scores[i][j]
            }

            dict_writer.writerow(row_as_dict)

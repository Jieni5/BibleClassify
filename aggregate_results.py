import pandas as pd
import re
import numpy as np

def make_chapter_dict(chapter_dict, predictions_eval_file, eval_sentences_file, txt_file, author_dict, predictions_file):

    # # Read evaluation sentences
    eval_sentences_df = pd.read_csv(eval_sentences_file, sep='\t')
   

    # # Read predictions
    predictions_df = pd.read_csv(predictions_eval_file, sep='\t')
    

    for i, row in predictions_df.iterrows():
        sentence = eval_sentences_df.iloc[i]['text']
        predicted_prob = row['prob']
        predicted_author = row['predicted']
        pattern = r"^([1-3]?\s?[A-Za-z]+(?:\s[A-Za-z]+)*)\s+(\d+):(\d+)\s*\t\s*(.+)$"
        with open(txt_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                match = re.match(pattern, line)
                if not match:
                    print("NO MATCH:", line)  # Debug
                    continue

                book, chapter, verse, verse_text = match.groups()
                book = re.sub(r"\s+", " ", book).strip()  # Replace multiple spaces with one


                clean = lambda s: re.sub(r"[\[\],;:.!?\"']", "", s).lower()#from chatgpt

                # Check if the sentence appears in the verse text
                if clean(sentence) in clean(verse_text):
                    for author, books in author_dict.items():
                        if book in books:
                            chapter_key = f"{book}{chapter}"
                            if chapter_key in chapter_dict[author]:
                                if 'Unknown' not in chapter_dict[author][chapter_key]:
                                    chapter_dict[author][chapter_key]['Unknown'] = []
                                if predicted_author not in chapter_dict[author][chapter_key]:
                                    chapter_dict[author][chapter_key][predicted_author] = []
                                if predicted_prob <= 0.25:
                                    chapter_dict[author][chapter_key]['Unknown'].append(predicted_prob)
                                chapter_dict[author][chapter_key][predicted_author].append(predicted_prob)
                                
    return chapter_dict

def aggregate_chapter_results(chapter_dict):
    aggregated_results = {}
    for author, chapters in chapter_dict.items():
        aggregated_results[author] = {}
        for chapter, auth_dict in chapters.items():
            unknown_probs = auth_dict.get("Unknown", [])
            total_sentences = sum(len(v) for v in auth_dict.values())
            unknown_count = len(unknown_probs)
            aggregated_results[author][chapter] = {}
            
            mostly_unknown = (unknown_count / total_sentences >= 0.60) if total_sentences > 0 else False
            aggregated_results[author][chapter]["MostlyUnknown"] = mostly_unknown

            if mostly_unknown:
                aggregated_results[author][chapter]["author"] = "Unknown"
                aggregated_results[author][chapter]["probability"] = (
                    np.mean(unknown_probs) if unknown_probs else None
                )
                continue
            
            author_prediction_counts = {
                a: len(p) for a, p in auth_dict.items()
                if a not in ["Unknown"] and len(p) > 0
            }

            if not author_prediction_counts:
                aggregated_results[author][chapter]["author"] = "Unknown"
                aggregated_results[author][chapter]["probability"] = None
                continue

            predicted_author = max(author_prediction_counts, key=author_prediction_counts.get)
            predicted_probs = auth_dict[predicted_author]

            aggregated_results[author][chapter]["author"] = predicted_author
            aggregated_results[author][chapter]["probability"] = np.mean(predicted_probs)

    return aggregated_results

def make_tsv(aggregated_results, output_file):
    rows = []
    for author, chapters in aggregated_results.items():
        for chapter, stats in chapters.items():

            # Skip incomplete chapters
            if "author" not in stats:
                continue

            # Guarantee a probability value in all cases
            prob = stats.get("probability")

            if prob is None:
                # If no probability exists but label is Unknown, give backup
                if stats["author"] == "Unknown":
                    prob = 0.0
                else:
                    prob = None

            rows.append([chapter, stats["author"], prob])

    df = pd.DataFrame(rows, columns=["chapter", "author", "probability"])
    df.to_csv(output_file, sep="\t", index=False)
        
def main():
    txt_file = "kjv_new_testament.txt"
    predictions_eval_file = "new_predictions_evaluate.tsv"
    eval_sentences_file = "evaluate_dataset.tsv"
    predictions_file = "predictions.tsv"
    #lists will contain the probability of the chapter
    author_dict = {"Matthew": ["Matthew"], "Mark": ["Mark"], "Luke": ["Luke", "Acts"], "John": ["John", "1 John", "2 John", "3 John", "Revelation"], "Paul": ["Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews"], "Peter": ["1 Peter", "2 Peter"], "James": ["James"], "Jude": ["Jude"]}
    
    chapter_dict = {"John": {"2 John1": {}, 
                             "3 John1": {}}, 
                    "Paul": { "Ephesians1": {}, "Ephesians2": {}, "Ephesians3": {},"Ephesians4": {}, "Ephesians5": {}, "Ephesians6": {}, 
                             "Colossians1": {}, "Colossians2": {}, "Colossians3": {}, "Colossians4": {}, "2 Thessalonians1": {}, 
                             "2 Thessalonians2": {},"2 Thessalonians3": {}, 
                             "1 Timothy1": {}, "1 Timothy2": {}, "1 Timothy3": {},"1 Timothy4": {}, "1 Timothy5": {}, "1 Timothy6": {}, "2 Timothy1": {}, 
                             "2 Timothy2": {}, "2 Timothy3": {}, "2 Timothy4": {}, 
                             "Titus1": {}, "Titus2": {}, "Titus3": {}, 
                             "Hebrews1": {}, "Hebrews2": {}, "Hebrews3": {}, "Hebrews4": {}, "Hebrews5": {}, "Hebrews6": {}, "Hebrews7": {}, "Hebrews8": {}, "Hebrews9": {}, "Hebrews10": {}, "Hebrews11": {}, "Hebrews12": {}, "Hebrews13": {}}, 
                    "Peter": {"2 Peter1": {}, "2 Peter2": {}, "2 Peter3": {}}}

    chapter_prob_dict = make_chapter_dict(chapter_dict, predictions_eval_file, eval_sentences_file, txt_file, author_dict, predictions_file)

    aggregated_results = aggregate_chapter_results(chapter_prob_dict)

    make_tsv(aggregated_results, output_file="new_aggregated_chapter_results.tsv")

if __name__ == '__main__':
    main()

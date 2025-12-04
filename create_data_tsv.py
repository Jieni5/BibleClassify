import re
import pandas as pd
import unicodedata

def merge_wrapped_verses(lines):
    merged = []
    current = ""
    verse_pattern = re.compile(r'^[1-3]?\s?[A-Za-z]+\s+\d+:\d+', re.IGNORECASE)

    for line in lines:
        line = unicodedata.normalize("NFKC", line)
        line = line.replace('\t', ' ').strip()
        if not line:
            continue

        if verse_pattern.match(line):

            if current:
                merged.append(current.strip())
            current = line
        else:

            current += " " + line

    if current:
        merged.append(current.strip())

    return merged

def file_read_in(filename) -> list:
    text_list = []
    with open(filename, "r") as f:
        raw_lines = f.readlines()

    text_list = merge_wrapped_verses(raw_lines)

    return text_list

def normalize_verse(verse):
    verse = unicodedata.normalize("NFKC", verse)
    verse = verse.replace('\t', ' ') #replace tabs with spaces and remove any leading whitespace
    verse = verse.strip()
    verse = re.sub(r'\s+', ' ', verse) #collapse multiple spaces
    
    return verse

def split_verse_into_sentences(verse_text):
    sentence_list = []
    sentence_list = list(filter(None, re.split(r'(?<=[.!?])\s+', verse_text)))
    return sentence_list

def make_data_dict(text_list, author_dict, certain_books, uncertain_books) -> dict:
    certain_author_sentences = {author: [] for author in author_dict}
    uncertain_author_sentences = {author: [] for author in author_dict}
    verse_pattern = re.compile(r'^\s*([1-3]?\s?[A-Za-z]+)\s+\d+:\d+\s*', re.IGNORECASE) #came from chatgpt
    book = None

    for verse in text_list:
        verse = normalize_verse(verse)
        
        verse_match = verse_pattern.match(verse)

        if verse_match:
            book = verse_match.group(1).replace(" ", "")
            verse_text = verse_pattern.sub('', verse, count = 1).lstrip()
        else:
            verse_text = verse

        sentences = split_verse_into_sentences(verse_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or sentence == "Amen.": #leave out Amen sentences
                continue
            for author, books in author_dict.items():
                if book in books:
                    if book in certain_books:
                        if author == "John": #oversample John
                            certain_author_sentences[author].extend([sentence] * 3)
                        elif author == "Luke" or author == "Peter": #oversample Luke and Peter
                            certain_author_sentences[author].extend([sentence] * 7)
                        elif author != "Paul": #oversample all certain authors except Paul
                            certain_author_sentences[author].extend([sentence] * 13)
                        else:
                            certain_author_sentences[author].append(sentence)
                    elif book in uncertain_books:
                        if author == "John": #oversample John
                            uncertain_author_sentences[author].extend([sentence] * 3)
                        elif author == "Luke" or author == "Peter": #oversample Luke and Peter
                            uncertain_author_sentences[author].extend([sentence] * 7)
                        elif author != "Paul": #oversample all certain authors except Paul
                            uncertain_author_sentences[author].extend([sentence] * 13)
                        else:
                            uncertain_author_sentences[author].append(sentence)
                    break

    return certain_author_sentences, uncertain_author_sentences

def split_data(certain_author_sentences) -> dict:
    certain_author_splits = {}
    for author, sentences in certain_author_sentences.items():
        n = len(sentences)
        split_point_1 = int(n * 0.8)
        split_point_2 = int(n * 0.9)
        certain_author_splits[author] = {"train": sentences[:split_point_1], "validate": sentences[split_point_1:split_point_2], "verify": sentences[split_point_2:]}
    return certain_author_splits

def make_data_csv(certain_author_splits, uncertain_author_sentences):
    train_data = {'label': [], 'text': [], 'textid': []}
    validate_data = {'label': [], 'text': [], 'textid': []}
    verify_data = {'target': [], 'text': [], 'textid': []}
    evaluate_data = {'target': [], 'text': [], 'textid': []}
    train_id = 0
    valid_id = 0
    verify_id = 0
    for author, splits in certain_author_splits.items():
        for sentence in splits["train"]:
            train_data["label"].append(author)
            train_data["text"].append(sentence)
            train_data["textid"].append(train_id)
            train_id += 1

        for sentence in splits["validate"]:
            print(f"valid id: {valid_id}")
            validate_data["label"].append(author)
            validate_data["text"].append(sentence)
            validate_data["textid"].append(valid_id)
            valid_id += 1

        for sentence in splits["verify"]:
            verify_data["target"].append(author)
            verify_data["text"].append(sentence)
            verify_data["textid"].append(verify_id)
            verify_id += 1
    
    evaluate_id = 0
    for author, sentences in uncertain_author_sentences.items():
        for sentence in sentences:
            print(f"evaluate id: {evaluate_id}")
            evaluate_data["target"].append(author)
            evaluate_data["text"].append(sentence)
            evaluate_data["textid"].append(evaluate_id)
            evaluate_id += 1

    df1 = pd.DataFrame(train_data)
    df1.to_csv('train_dataset.tsv', sep='\t', index=False)
    df2 = pd.DataFrame(validate_data)
    df2.to_csv('validate_dataset.tsv', sep='\t', index=False)
    df3 = pd.DataFrame(verify_data)
    df3.to_csv('verify_dataset.tsv', sep='\t', index=False)
    df4 = pd.DataFrame(evaluate_data)
    df4.to_csv('evaluate_dataset.tsv', sep='\t', index=False)


def main():
    txt_file = "kjv_new_testament.txt"
    author_dict = {"Matthew": ["Matthew"], "Mark": ["Mark"], "Luke": ["Luke", "Acts"], "John": ["John", "1John", "2John", "3John", "Revelation"], "Paul": ["Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1Thessalonians", "2Thessalonians", "1Timothy", "2Timothy", "Titus", "Philemon", "Hebrews"], "Peter": ["1Peter", "2Peter"], "James": ["James"], "Jude": ["Jude"]}
    certain_books = ["James", "Jude", "Matthew", "Mark", "Luke", "Acts", "John", "1John", "Revelation", "Romans", "1Corinthians", "2Corinthians", "Galatians", "Philippians", "1Thessalonians", "Philemon", "1Peter"]
    uncertain_books = ["1Timothy", "2Timothy", "Titus", "Hebrews", "2Peter", "2John", "3John", "Ephesians", "Colossians", "2Thessalonians"]
    text_lst = file_read_in(txt_file)
    
    certain_author_sentences, uncertain_author_sentences = make_data_dict(text_lst, author_dict, certain_books, uncertain_books)

    author_splits = split_data(certain_author_sentences)
    
    make_data_csv(author_splits, uncertain_author_sentences)

if __name__ == '__main__':
    main()

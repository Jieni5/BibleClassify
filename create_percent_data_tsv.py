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

def make_data_dict(text_list, author_dict) -> dict:
    author_sentences = {author: [] for author in author_dict}
    verse_pattern = re.compile(r'^\s*([1-3]?\s?[A-Za-z]+)\s+\d+:\d+\s*', re.IGNORECASE)
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
            if not sentence:
                continue
            for author, books in author_dict.items():
                if book in books:
                    author_sentences[author].append(sentence)
                
                    break

    return author_sentences

def split_data(author_sentences) -> dict:
    author_splits = {}
    for author, sentences in author_sentences.items():
        n = len(sentences)
        split_point_1 = int(n * 0.8)
        split_point_2 = int(n * 0.9)
        author_splits[author] = {"train": sentences[:split_point_1], "validate": sentences[split_point_1:split_point_2], "verify": sentences[split_point_2:]}
    return author_splits

def make_data_csv(author_splits):
    train_data = {'Author': [], 'Sentence': []}
    validate_data = {'Author': [], 'Sentence': []}
    verify_data = {'Author': [], 'Sentence': []}
    for author, splits in author_splits.items():
        for sentence in splits["train"]:
            train_data["Author"].append(author)
            train_data["Sentence"].append(sentence)

        for sentence in splits["validate"]:
            validate_data["Author"].append(author)
            validate_data["Sentence"].append(sentence)

        for sentence in splits["verify"]:
            verify_data["Author"].append(author)
            verify_data["Sentence"].append(sentence)

    df1 = pd.DataFrame(train_data)
    df1.to_csv('train_dataset.tsv', sep='\t', index=False)
    df2 = pd.DataFrame(validate_data)
    df2.to_csv('validate_dataset.tsv', sep='\t', index=False)
    df3 = pd.DataFrame(verify_data)
    df3.to_csv('verify_dataset.tsv', sep='\t', index=False)


def main():
    txt_file = "kjv_new_testament.txt"
    author_dict = {"Matthew": ["Matthew"], "Mark": ["Mark"], "Luke": ["Luke", "Acts"], "John": ["John", "1John", "2John", "3John", "Revelation"], "Paul": ["Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians"], "Peter": ["1Peter", "2Peter"], "James": ["James"], "Jude": ["Jude"]}
    text_lst = file_read_in(txt_file)
    
    author_sentences = make_data_dict(text_lst, author_dict)

    author_splits = split_data(author_sentences)
    
    make_data_csv(author_splits)

if __name__ == '__main__':
    main()

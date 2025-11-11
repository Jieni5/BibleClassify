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

def make_data_lists(text_list, author_dict) -> list:
    author_lst = []
    sent_lst = []
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
                    author_lst.append(author)
                
                    sent_lst.append(sentence)
                
                    break
    return author_lst, sent_lst

def make_data_csv(author_lst, sent_lst):
    data = {'Author': author_lst, 'Sentence': sent_lst}
    df = pd.DataFrame(data)
    df.to_csv('full_dataset.tsv', sep='\t', index=False)

def check_sentence_number(sent_lst, text_list):
    verse_pattern = re.compile(r'^[1-3]?\s?[A-Za-z]+\s+\d+:\d+\s*')

    unmatched_originals = 0
    for sentence in text_list:
        cleaned = verse_pattern.sub('', sentence, count=1).strip()
        if cleaned not in sent_lst:
            unmatched_originals += 1
            print("Not found in sent_lst:", sentence)

    print(f"{unmatched_originals} lines from text_list not found in sent_lst.")

def find_unmatched_lines(sent_lst, text_list):
    unmatched = []
    for verse in text_list:
        verse_text = re.sub(r'^[1-3]?\s?[A-Za-z]+\s+\d+:\d+\s*', '', verse).strip()
        # Split verse into sentences
        sentences = split_verse_into_sentences(verse_text)
        for s in sentences:
            if s not in sent_lst:
                unmatched.append(s)
    return unmatched

def main():
    txt_file = "kjv_new_testament.txt"
    author_dict = {"Matthew": ["Matthew"], "Mark": ["Mark"], "Luke": ["Luke", "Acts"], "John": ["John", "1John", "2John", "3John", "Revelation"], "Paul": ["Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians"], "Peter": ["1Peter", "2Peter"], "James": ["James"], "Jude": ["Jude"]}
    text_lst = file_read_in(txt_file)
    
    verse_pattern = re.compile(r'^\s*([1-3]?\s?[A-Za-z]+)\s+\d+:\d+\s*', re.IGNORECASE)
    author_lst, sent_lst = make_data_lists(text_lst, author_dict)
    
    make_data_csv(author_lst, sent_lst)

if __name__ == '__main__':
    main()

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
    # text_list = []
    # buffer = ''
    # verse_pattern = re.compile(r'^[1-3]?\s?[A-Za-z]+\s\d+:\d+\s*')
    
    # with open(filename, "r") as f:
    #     for line in f:
    #         line = line.replace('\t', ' ').strip()
    #         # line = line.strip()
    #         line_list = list(filter(None, re.split(r'(?<=[.!?])\s*', line)))
    #         #print(line_list)
    #         #text_list.append(line_list)
    #         for sentence in line_list:
    #             if buffer:
    #                 sentence = verse_pattern.sub('', sentence)
    #                 sentence = buffer + ' ' + sentence
    #                 buffer = ''
    #             if not sentence or sentence[-1] in ":;,":
    #                 buffer = sentence
    #             else:
    #                 text_list.append(sentence)
    #     if buffer:
    #         text_list.append(buffer)
        
    # return text_list

def normalize_line(line):
    import unicodedata, re
    line = unicodedata.normalize("NFKC", line)
    line = line.replace('\t', ' ').strip()
    line = re.sub(r'\s+', ' ', line)
    return line

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
        verse = unicodedata.normalize("NFKC", verse)
        verse = verse.replace('\t', ' ') #replace tabs with spaces and remove any leading whitespace
        verse = verse.strip()
        verse = re.sub(r'\s+', ' ', verse) #collapse multiple spaces

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
        
        
    # for s in sent_lst:
    #     if re.search(r'^[1-3]?\s?[A-Za-z]+\s+\d+:\d+', s):
    #         print("Still has reference:", s)
    
    return author_lst, sent_lst

def make_data_csv(author_lst, sent_lst):
    # print("Test2")
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
    # verse_pattern = re.compile(r'^\s*([1-3]?\s?[A-Za-z]+)\s+\d+:\d+', re.IGNORECASE)
    # missing = []

    # for sentence in text_list:
    #     sentence = sentence.strip()
    #     verse_match = verse_pattern.match(sentence)

    #     if not verse_match:
    #         missing.append(sentence)
    #     else:
    #         book = verse_match.group(1).replace(" ", "")
    #         if not any(book in books for books in author_dict.values()):
    #             missing.append(sentence)

    # print(f"{len(missing)} lines skipped or unmatched:")
    # for line in missing[:20]:  # show first 20 examples
    #     print("  ", line)

def main():
    txt_file = "kjv_new_testament.txt"
    author_dict = {"Matthew": ["Matthew"], "Mark": ["Mark"], "Luke": ["Luke", "Acts"], "John": ["John", "1John", "2John", "3John", "Revelation"], "Paul": ["Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians"], "Peter": ["1Peter", "2Peter"], "James": ["James"], "Jude": ["Jude"]}
    text_lst = file_read_in(txt_file)
    #text_list = split_into_sentences(text_lst)
    #verse_pattern = re.compile(r'^[1-3]?\s?[A-Za-z]+\s\d+:\d+\s*')
    verse_pattern = re.compile(r'^\s*([1-3]?\s?[A-Za-z]+)\s+\d+:\d+\s*', re.IGNORECASE)
    author_lst, sent_lst = make_data_lists(text_lst, author_dict)
    # normalized_text_list = [normalize_line(verse_pattern.sub('', line)) for line in text_lst]
    # normalized_sent_lst = [normalize_line(line) for line in sent_lst]

    # missing_lines = [line for line in normalized_text_list if line not in normalized_sent_lst]



    # missing_lines = []

    # for line in normalized_text_list:
    #     if line not in normalized_sent_lst:
    #         missing_lines.append(line)

    # print(f"{len(missing_lines)} lines unmatched!")
    # for line in missing_lines[:20]:  # print first 20 for inspection
    #     print(line)

    #check_sentence_number(sent_lst, text_list)
    # unmatched = find_unmatched_lines(sent_lst, text_lst)
    # if unmatched:
    #     print(f"{len(unmatched)} lines unmatched!")
    #     for line in unmatched[:20]:  # Show only first 20 for brevity
    #         print(line)
    # else:
    #     print("All lines matched successfully!")
    make_data_csv(author_lst, sent_lst)

if __name__ == '__main__':
    main()
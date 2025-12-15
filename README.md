# BibleClassify: New Testament Authorship Prediction
### Sylvia Guo, Morgan Morel, Jieni Wu  
Colgate University · Fall 2025

# Overview

This repository contains the full code, configuration files, and dataset preparation steps used to reproduce our project on predicting authorship in the New Testament using DistilBERT and the NLPScholar framework.

The project trains a transformer model on books with known authorship, evaluates it on both known and debated books, and aggregates sentence-level predictions into chapter-level authorship probabilities.

## Repository Structure
BibleClassify:
- config/ # NLPScholar YAML configs
  - train.yaml # Fine-tuning configuration
  - verify.yaml # Evaluation on verification set (known authors)
  - evaluate.yaml # Evaluation on debated books (unknown authors)
- data/ # Generated TSV datasets (train/val/verify/evaluate)
- results/ # Old aggregated results
- results_new/ # Updated aggregated results (0.60 chapter threshold)
- Literature/ # Supporting readings
- create_data_tsv.py # Converts raw KJV text into TSV datasets
- aggregate_results.py # Aggregates predictions into chapter-level results
- dataset_template.py # Helper functions for TSV formatting
- kjv_new_testament.txt # Full KJV text used for dataset creation
- train_dataset.tsv # Processed training data
- evaluate_dataset.tsv # Processed evaluation data



Take probability of text over sentences >60% then assign to the author model classified it to other wise assign to unknown author
Why we chose 60%(some paper will be needed to prove why this number is significant), prove methodology to audience, high probability of unknown author(either our model doesn't work or there's a significant number of unknown authors)
Average of the results for each sentence is the result for the book overall(some paper/article proving why using the average is accurate enough to use as the overall answer), assign a value to the author and a value to the unknown label and get the average to determine which one sentences were assigned to the most, OR would be easier get average of book based on sentence probabilities and if that average >60% assign book to author and if not assign book to unknown label
Contribution, motivation, how does this add to the literature?
The literature has yet to look at the text beyond using syntactic parsing and other methods similar to n-gram models. This experiment could show that there's significant evidence for theories that already exist that certain books are not written by a known author/the author they're attributed to. This experiment is geared towards the Christian community and therefore will need to be strong in its methodology and results.

We are using bayesian classification model to determine the authors of the books in the Bible

the sequence of steps:
1. compiling the dataset: We have a format of the whole New Testament that can be read through and transformed into a tsv file with two columns: sentences and authors.

3. splitting the dataset: We will need to split the tsv file we had into two main parts: training and testing. for the training, we will also need to split that into three parts: training, validation, and verification. (maybe 80%, 10%, 10%)

5. Trian/Finetune: We will then finetune based on our chosen text classification model using our train & validate datasets.

6. verify: We will verify if our model works using the verification dataset.

7. test: We will then evaluate the uncertain books using our finetuned model. We will get predictions from this test for each sentence.

8. calculate: We will then take the average result of the sentences for each book and use this as the result for the book.

9. compare: We will then compare the predictions our model outputs to the biblical scholar's general ideas using papers we collected before. We're looking to see whether and what the differences are between our results and biblical scholar's theories.

10. reflect: we will then reflect based on the output of our comparison. 


## NLPScholar output
- Running 'analysis' mode, the output will show different categories (different known authors), and the probability of the text being classified into this category.

- We will have authors assigned to texts only if the probability is over 60% and otherwise will assign an unknown class label to the text in question.

- A table could be created with the rows being different authors for known chapters, and columns being titles of unknown chapters. The boxes would be the probabilities of the author writing this chapter.

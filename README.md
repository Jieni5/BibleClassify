# BibleClassify
We are using text classification model to determine the authors of the books in the Bible

the sequence of steps:
1. compiling the dataset: we will need to find a format of the whole New Testament that can be read through and transformed into a tsv file with two columns: sentences and authors.

3. splitting the dataset: we will need to split the tsv file we had into two main parts: training and testing. for the training, we will also need to split that into three parts: training, validation, and verification. (maybe 80%, 10%, 10%)

5. Trian/Finetune: we will then finetune based on our chose casual model using our train & val dataset.

6. verify: we will verify if our model works using the verification dataset.

7. test: we will then evaluate the uncertain books using our finetuned model. we will get predictions from this test for each sentences.

8. compare: we will then compare the predictions our model output to the biblical scholar's general ideas using papers we collected before.

9. reflect: we will then reflect based on the output of our comparison. 

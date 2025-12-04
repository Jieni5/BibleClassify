import pandas as pd


df = pd.read_csv('../data/predictions_verify.tsv', sep='\t')


filtered_df = df[df['prob'] > 0.25]

filtered_df = filtered_df[['textid', 'target', 'predicted', 'prob']]


filtered_df.to_csv('filtered_predictions_verify.tsv', sep='\t', index=False)

print("\nFiltered data saved to 'filtered_predictions_verify.tsv'")

accuracy_data = []
for name in ['Matthew', 'Luke', 'John', 'Paul', 'Peter','James', 'Jude']:
    # Filter by target name
    target_df = filtered_df[filtered_df['target'] == name]
    
    if len(target_df) > 0:
        # Calculate percentage where target == predicted
        correct = (target_df['target'] == target_df['predicted']).sum()
        total = len(target_df)
        percentage = (correct / total) * 100
        
        accuracy_data.append({
            'target': name,
            'percentage_correct': round(percentage, 2)
        })
    else:
        accuracy_data.append({
            'target': name,
            'percentage_correct': 0.0
        })

accuracy_df = pd.DataFrame(accuracy_data)
accuracy_df.to_csv('accuracy_by_target_verify.tsv', sep='\t', index=False)
print("\nAccuracy analysis saved to 'accuracy_by_target_verify.tsv'")
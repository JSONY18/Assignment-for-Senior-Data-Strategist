import os
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Import the cleaning function from your label_map script
from label_map import verify_and_clean_datapack, OUTPUT_DIR

# 2. Run the function to get the required DataFrames into this script's scope
site_inv, pii_det, licenses, sharing_links = verify_and_clean_datapack()

# Recreate 'merged_risk' exactly how it's done in your cleaning script
import pandas as pd
merged_risk = pd.merge(site_inv, pii_det, on='site_id', how='left')
merged_risk['match_count_clean'] = merged_risk['match_count_clean'].fillna(0).astype(int)
merged_risk['copilot_accessible'] = merged_risk['new_label'].isin(['Public', 'Internal', 'Unlabeled'])

# ----------------------------------------------------------------
# Plotting & Visualization
# ----------------------------------------------------------------

# Set style
sns.set_theme(style="whitegrid")

# --- Plot 1: Label coverage data ---
labels_df = site_inv['new_label'].value_counts().reset_index()
labels_df.columns = ['Label', 'Count']

plt.figure(figsize=(8, 5))
sns.barplot(x='Count', y='Label', data=labels_df, palette='viridis')
plt.title('Current SharePoint/OneDrive Site Label Coverage (New Taxonomy Mapped)')
plt.xlabel('Number of Sites')
plt.ylabel('Sensitivity Label')
plt.tight_layout()

# Save directly to the output folder using os.path.join
plt.savefig(os.path.join(OUTPUT_DIR, 'label_coverage.png'), dpi=300)
plt.close()

# --- Plot 2: Copilot Risk ---
accessible_sensitive = merged_risk[merged_risk['copilot_accessible'] & (merged_risk['match_count_clean'] > 0)].copy()

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=accessible_sensitive, 
    x='site_id', 
    y='match_count_clean', 
    hue='detection_type', 
    size='match_count_clean',
    sizes=(100, 1000),
    palette='Set2'
)
plt.title('Copilot Leak Vectors: Sensitive Content Accessible by Copilot')
plt.xlabel('Site ID')
plt.ylabel('PII/Sensitive Match Count')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Save directly to the output folder using os.path.join
plt.savefig(os.path.join(OUTPUT_DIR, 'copilot_risks.png'), dpi=300)
plt.close()

print(f"🎯 Visualizations created successfully and saved to: {OUTPUT_DIR}")
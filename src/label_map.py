import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define path of the directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define data and output paths location
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../data"))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../output"))

def verify_and_clean_datapack():
    print("Initializing Legislative Assembly Data Pack Verification...")
    
    # ----------------------------------------------------
    # 1. LOAD DATA PACK
    # ----------------------------------------------------
    site_inv = pd.read_csv(f"{DATA_DIR}/site_inventory.csv")
    pii_det = pd.read_csv(f"{DATA_DIR}/pii_detections.csv")
    licenses = pd.read_csv(f"{DATA_DIR}/license_assignments.csv")
    sharing_links = pd.read_csv(f"{DATA_DIR}/sharing_links.csv")

    # ----------------------------------------------------
    # 2. CLEAN DATA PACK (Moved inside the function scope)
    # ----------------------------------------------------
    # --- 1. Clean site_inventory.csv ---
    # Drop the summary row at the bottom
    site_inv = site_inv[site_inv['site_id'].str.startswith('S-')]

    # Clean column headers
    site_inv.columns = site_inv.columns.str.strip()

    # Map old labels to new taxonomy
    label_map = {
        'Public': 'Public',
        'Internal': 'Internal',
        'General': 'Public', # General maps to Public default based on Public Job Postings
        'Confidential': 'Confidential',
        'Restricted': 'Restricted',
        'Confidential / All Employees': 'Internal', # All employees means everyone with an account
        'Confidential / Anyone (not protected)': 'Internal',
        'Confidential / Trusted People': 'Confidential',
        'Highly Confidential / Specific People': 'Restricted'
    }
    site_inv['new_label'] = site_inv['current_label'].map(label_map).fillna('Unlabeled')
    
    # ----------------------------------------------------
    # FIX: Overwrite 'Unlabeled' if it contains sensitive keywords
    # ----------------------------------------------------
    # Check for keywords in the site name (case-insensitive)

    sensitive_keywords = 'payroll|sin|pii_bundle|records|member'
    is_unlabeled = site_inv['new_label'] == 'Unlabeled'
    has_sensitive_text = site_inv['site_name'].str.contains(sensitive_keywords, case=False, na=False)

    site_inv.loc[is_unlabeled & has_sensitive_text, 'new_label'] = 'Confidential'

    # --- 2. Clean pii_detections.csv ---
    # Drop explicit duplicates (like row 17 for S-003)
    pii_det = pii_det.drop_duplicates(subset=['site_id', 'detection_type', 'match_count', 'sample_context'])

    # Handle non-numeric match counts
    pii_det['match_count_clean'] = pii_det['match_count'].astype(str).str.strip()
    pii_det['match_count_clean'] = pii_det['match_count_clean'].replace({'many': '5000', 'nan': '0'})
    pii_det['match_count_clean'] = pd.to_numeric(pii_det['match_count_clean'], errors='coerce').fillna(0).astype(int)

    # --- 3. Clean license_assignments.csv ---
    licenses['last_signin_clean'] = licenses['last_signin'].replace(['never', 'Never'], np.nan)
    licenses['last_signin_clean'] = pd.to_datetime(licenses['last_signin_clean'], errors='coerce')
    licenses['department'] = licenses['department'].fillna('Unknown / Unassigned')

    # --- 4. Analyze Label Coverage ---
    coverage = site_inv['new_label'].value_counts()
    print("New Label Coverage counts:\n", coverage)

 # --- 5. Analyze Copilot Risk Surface ---
    # Group pii_det by site_id first to combine match counts and avoid duplicating site rows
    pii_det_grouped = pii_det.groupby('site_id').agg({
        'match_count_clean': 'sum',
        'detection_type': lambda x: ', '.join(x.unique()) # Combines types into a single string
    }).reset_index()

    # Now merge site inventory with the aggregated PII data
    merged_risk = pd.merge(site_inv, pii_det_grouped, on='site_id', how='left')
    merged_risk['match_count_clean'] = merged_risk['match_count_clean'].fillna(0).astype(int)

    # Refined deduplication
    pii_det_clean = pii_det.drop_duplicates(subset=['site_id', 'detection_type', 'match_count'])

    # Remerge
    merged_risk = pd.merge(site_inv, pii_det_clean, on='site_id', how='left')
    merged_risk['match_count_clean'] = merged_risk['match_count_clean'].fillna(0).astype(int)
    merged_risk['copilot_accessible'] = merged_risk['new_label'].isin(['Public', 'Internal', 'Unlabeled'])

    print(merged_risk[['site_id', 'site_name', 'new_label', 'detection_type', 'match_count_clean', 'has_anonymous_links']])

    # Identify where Copilot can reach sensitive files
    merged_risk['copilot_accessible'] = merged_risk['new_label'].isin(['Public', 'Internal', 'Unlabeled'])

    print("\nSensitive detections accessible by Copilot (Aggregated):")
    sharing_col = 'sharing_exposure' if 'sharing_exposure' in merged_risk.columns else 'has_anonymous_links'
    accessible_pii = merged_risk[merged_risk['copilot_accessible'] & (merged_risk['match_count_clean'] > 0)]
    print(accessible_pii[['site_id', 'site_name', 'new_label', 'detection_type', 'match_count_clean', sharing_col]])
    # Optional: Return dataframes if you need them later outside the function
    return site_inv, pii_det, licenses, sharing_links

# Execute the function
if __name__ == "__main__":
    site_inv, pii_det, licenses, sharing_links = verify_and_clean_datapack()
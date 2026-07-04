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
    site_inv = pd.read_csv(f"{DATA_DIR}/site_inventory.csv", encoding="utf-8")
    pii_det = pd.read_csv(f"{DATA_DIR}/pii_detections.csv")
    licenses = pd.read_csv(f"{DATA_DIR}/license_assignments.csv")
    sharing_links = pd.read_csv(f"{DATA_DIR}/sharing_links.csv")

    # ----------------------------------------------------
    # 2. CLEAN & VERIFY LICENSE DATA
    # ----------------------------------------------------
    print("\n🧹 Cleaning license_assignments.csv...")

    # Fix Issue 1: Handle missing values in the 'department' column
    if 'department' in licenses.columns:
        missing_dept_count = licenses['department'].isna().sum()
        print(f" - Found {missing_dept_count} rows with missing departments. Filling with 'Unknown'.")
        licenses['department'] = licenses['department'].fillna('Unknown')
    
    # Fix Issue 2: Clean 'last_signin', replace "never" with NULL, and enforce DateTime format
    if 'last_signin' in licenses.columns:
        licenses['last_signin_clean'] = licenses['last_signin'].replace(to_replace=r'(?i)^never$', value=np.nan, regex=True)
        licenses['last_signin_clean'] = pd.to_datetime(licenses['last_signin_clean'], errors='coerce')
        stale_or_never_count = licenses['last_signin_clean'].isna().sum()
        print(f" - Standardized 'last_signin' to DateTime. {stale_or_never_count} users have NULL/Never signed in.")

    # Fix Issue 3: LICENSING AUDIT & COST BREAKDOWN, only E7 licensing and active are Copilot-eligible 
    if 'account_status' in licenses.columns and 'license_sku' in licenses.columns:
        # Standardize formatting to avoid casing bugs
        licenses['account_status'] = licenses['account_status'].astype(str).str.strip().str.lower()
        licenses['license_sku'] = licenses['license_sku'].astype(str).str.strip().str.upper()

        # Track cohorts
        active_e7 = licenses[(licenses['account_status'] == 'active') & (licenses['license_sku'] == 'E7')]
        active_e5 = licenses[(licenses['account_status'] == 'active') & (licenses['license_sku'] == 'E5')]
        active_e3 = licenses[(licenses['account_status'] == 'active') & (licenses['license_sku'] == 'E3')]

        print(f" --- LICENSING AUDIT SUMMARY ---")
        print(f"  ✅ True Active Copilot-Eligible (E7): {active_e7.shape[0]} staff.")
        print(f"  💰 Active E5 Tier Count (Needs Upgrade): {active_e5.shape[0]} staff.")
        print(f"  💰 Active E3 Tier Count (Needs Upgrade): {active_e3.shape[0]} staff.")
        print(f"  [AUDIT] Total Active Staff: {licenses[licenses['account_status'] == 'active'].shape[0]} / 900 claimed.\n")       
    
    # ----------------------------------------------------
    # 3. CLEAN DATA PACK FOR SITE_INVENTORY
    # ----------------------------------------------------
    # --- 1. Clean site_inventory.csv ---
        print("\n🧹 Cleaning site_inventory.csv...")

    # Fix Issue 4: Remove the total summary row at the bottom
    site_inv = site_inv[site_inv['site_id'].str.startswith('S-')]

    # Fix Issue 5: enable utf-8 to handle encoding anomalies such as "Hansard â€“ Broadcast Ops
    site_inv.columns = site_inv.columns.str.strip()

    # Fix Issue 6: Clean and standardize date format to ISO-8601 on last_modified column
    if 'last_modified' in site_inv.columns:
        # Coerce invalid parsing into NaT/null values, then build uniform YYYY-MM-DD representations
        converted_dates = pd.to_datetime(site_inv['last_modified'], errors='coerce')
        site_inv['last_modified'] = converted_dates.dt.strftime('%Y-%m-%d')
        print(f" - Standardized 'last_modified' column to ISO-8601 format.")

   # Fix Issue 7: Map old labels to the Assembly’s four labels and descriptors
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

    # ----------------------------------------------------
    # 4. CLEAN DATA PACK FOR PII_DETECTIONS
    # ----------------------------------------------------
    # --- 1. Clean pii_detections.csv ---
    print("\n🧹 Cleaning pii_detections.csv...")

    # Fix Issue 8: Drop explicit duplicates (like row 19 for S-003)
    pii_det = pii_det.drop_duplicates(subset=['site_id', 'detection_type', 'match_count', 'sample_context'])

    # Handle non-numeric match counts
    pii_det['match_count_clean'] = pii_det['match_count'].astype(str).str.strip()
   # Fix Issue 9: Clean up textual exceptions (like "many" in S-099) before turning column numeric as 5000
   # Fix Issue 10: Identify and resolve missing/empty values in match_count, set it as 0 
    pii_det['match_count_clean'] = pii_det['match_count_clean'].replace({'many': '5000', 'nan': '0'})
    pii_det['match_count_clean'] = pd.to_numeric(pii_det['match_count_clean'], errors='coerce').fillna(0).astype(int)

    # --- 3. Clean license_assignments.csv ---
    licenses['last_signin_clean'] = licenses['last_signin'].replace(['never', 'Never'], np.nan)
    licenses['last_signin_clean'] = pd.to_datetime(licenses['last_signin_clean'], errors='coerce')
    licenses['department'] = licenses['department'].fillna('Unknown / Unassigned')

    # ----------------------------------------------------
    # 5. CLEAN DATA PACK FOR SHAREING LINKS
    # ----------------------------------------------------
    # --- 1. Clean sharing_links.csv ---
    print("\n🧹 Cleaning sharing_links.csv...")

   # Fix Issue 11: Flag logical contradictions (Anonymous links with a target domain)
    contradictory_links = sharing_links[(sharing_links['link_type'] == 'anonymous') & (sharing_links['target_external_domain'] != '(any)')]

    # Fix Issue 12: Flag broken specific invitations (Specific type with missing target domain)
    broken_specific_links = sharing_links[(sharing_links['link_type'] == 'specific') & (sharing_links['target_external_domain'].isna())]

    # Fix Issue 13:Standardize text placeholders to clean null handling
    sharing_links['target_external_domain'] = sharing_links['target_external_domain'].fillna('NOT_APPLICABLE')

    print("Review required for Contradictions:\n", contradictory_links)
    print("Review required for Broken Invites:\n", broken_specific_links)

    # ----------------------------------------------------
    # 6. ANALYZE LABEL COVERAGE AND RISK SURFACE
    # ----------------------------------------------------
    # --- 1. Analyze Label Coverage ---
    coverage = site_inv['new_label'].value_counts()
    print("New Label Coverage counts:\n", coverage)

    # --- 2. Analyze Copilot Risk Surface ---
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
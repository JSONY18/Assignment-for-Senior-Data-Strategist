# Conceptual framework for your data cleaning notebook
import pandas as pd

# 1. Load Data Pack
site_inv = pd.read_csv('../data/site_inventory.csv')
pii_det = pd.read_csv('../data/pii_detections.csv')
licenses = pd.read_csv('../data/license_assignments.csv')

# 2. Verify Claims
true_licensed_staff = licenses[licenses['status'] == 'Active'].shape[0]
print(f"Verified Active Licenses: {true_licensed_staff} vs Claimed: 900")

# 3. Filter False Positives & Map Taxonomy
# Remove legacy/incorrect BC Gov labels and flag for compliance mapping
site_inv['corrected_label'] = site_inv['current_label'].replace({
    'Protected A': 'Internal',
    'Protected B': 'Confidential',
    'Protected C': 'Restricted'
})

# 4. Identify Over-shared Content (The Copilot Threat Vector)
# Merge sharing links with PII data to highlight active exposure points
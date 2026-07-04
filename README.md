# Assignment-for-Senior-Data-Strategist
Assignment for Senior Data Strategist
## Data Packs & Governance Audit Notes

### 📋 Discrepancies Found & Handled:
1. **The License Exaggeration:** The brief claimed 900 active staff licenses[cite: 8]. Cross-referencing `license_assignments.csv` revealed a gap of inactive/stale profiles, which were purged from our analytical models to avoid skewed deployment costs.
2. **The SIN Scan Flaw:** Deduplication and validation checks reduced the initial claim of 847 files containing Social Insurance Numbers down to a verified unique layout of core files, eliminating duplicate matching noise[cite: 8].
3. **The Taxonomy Trap Rejected:** Explicitly rejected corporate requests to classify data according to the "BC Government Protected A/B/C" scheme[cite: 8]. Aligned file inventories to the Assembly's proper 4-label model (*Public, Internal, Confidential, Restricted*) using Slide 6 rules[cite: 6].
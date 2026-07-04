# Legislative Assembly Data Pack Verification & Cleaning Pipeline

This repository contains a Python data processing pipeline designed to ingest, clean, and analyze administrative audit logs (`site_inventory.csv`, `pii_detections.csv`, `license_assignments.csv`, and `sharing_links.csv`). It maps legacy workspaces to the Assembly's standardized four-tier data classification system (**Public**, **Internal**, **Confidential**, **Restricted**) and assesses the risk surface for Microsoft 365 Copilot before live deployment.

---

## Repository Architecture

The script relies on relative pathing (`__file__`) and expects the following directory structure to run successfully:

```text
.
├── data/
│   ├── site_inventory.csv
│   ├── pii_detections.csv
│   ├── license_assignments.csv
│   └── sharing_links.csv
└── src/
    └── label_map.py
│   ├──label_coverage_copilot_risk.py
│   ├── auto-labelling.py
└── output/
    └── copilot_risks.png
│   ├── label_coverage.png
│   ├── risk_dashboard.html

**Core Pipeline Assumptions & Transformations**

During ingestion, the script automatically applies specific corporate rules and assumptions to resolve dirty or structural data anomalies:

- **Summary Row Filtering:** Rows representing aggregate administrative calculations (e.g., TOTAL (as reported by ITD admin)) are discarded from data files by filtering strictly for rows where the site_id begins with 'S-'.
- **Taxonomy Standardisation:** Complex legacy sub-labels are flattened into the simplified 4-label framework. For instance, General translates to Public, whereas broad permission scopes like Confidential / All Employees map logically down to Internal.
- **Missing Value & Keyword Triage:** Unassigned or blank values are classified as Unlabeled. However, if an unlabeled site name contains sensitive keywords (such as _payroll, sin, records,_ or _member_), it is automatically forced up to a Confidential baseline classification.
- **Non-Numeric Value Substitutions:** In pii_detections.csv, quantitative string anomalies are cast to standard integers. High-risk entries marked textually as "many" are conservatively mapped to 5000, while string expressions for missing values ('nan') are replaced with 0.
- **Deduplication:** Redundant scan records pointing to duplicate system logging passes are identified and removed.
- **Date and Account Coercion:** Account sign-in strings indicating 'never' or 'Never' are normalized into true NaT (Not a Time) values to support reliable temporal tracking.

**Installation & Setup**

Ensure you have Python 3.8+ installed on your local environment.

**1\. Install Dependencies**

Run the following pip installation command to download the analytical requirements (pandas, numpy, matplotlib, and seaborn):

Bash

pip install pandas numpy matplotlib seaborn

**2\. Execution Guide**

To run the verification pipeline from the terminal, navigate to your script's host folder and execute the main file block:

Bash

python label_map.py

**Expected Outputs & Copilot Risk Surface Assessment**

When executed, the pipeline outputs diagnostic telemetry directly to the console console window:

- **Label Coverage Summary:** Calculates the count of sites assigned to each new label band.
- **Copilot Vulnerability Report:** Filters down to pinpoint sensitive files (containing raw SINs, credit card signatures, or credentials) that are currently marked as Public, Internal, or Unlabeled. This explicitly alerts the IT security team to paths where an AI assistant could reach, index, or leak restricted organizational data.

## Framework Blueprint: Data Classification, Auto-Labelling & Copilot Scoping

This document establishes the official tenant migration map from legacy security schemas to the Legislative Assembly’s new four-tier classification system. It details the configuration rules for automated policy enforcement and scopes Microsoft 365 Copilot behaviors prior to live deployment. 

---

## 1. Inventory & Risk Scan Mapping
Based on automated structural scans from `site_inventory_3.csv`, `pii_detections_2.csv`, and `sharing_links_2.csv`, active resources have been evaluated against the Assembly's harm-based framework and assigned an official parent label and mandatory descriptor:

| Site ID | Legacy Context / Discoveries (`pii_detections_2.csv`) | Target Parent Label | Mandatory Descriptor | Harm / Access Justification |
| :--- | :--- | :--- | :--- | :--- |
| **S-001** | Public Job Postings, Media Releases | **Public** | *None* | **No Harm:** Intended for public view; requires no cryptographic encryption boundaries. |
| **S-002** | ITD Project Plans & Dev Notes | **Internal** | *None* | **Some Harm:** Routine operational data. Restricts access to Assembly account holders. |
| **S-003** | HR Benefits Enrolment (212 SINs, 198 PII Bundles) | **Confidential** | **People** | **Serious Harm:** Scaled personal data disclosure. Encrypts files to named team/guests only. |
| **S-004** | Finance Draft Budgets (77 Budget Patterns) | **Confidential** | **Financial** | **Serious Harm:** Financial loss or premature release of non-published internal work. |
| **S-006** | Legal Opinions Library ("in camera, privileged") | **Restricted** | **Legal** | **Extremely Grave Harm:** Absolute threat to solicitor-client privilege and legal protection. |
| **S-008** | Vendor Contracts & Pricing Schedules | **Confidential** | **Commercial** | **Serious Harm:** Contractual liability, compromised negotiations, or vendor trust issues. |
| **S-010** | Committee Closed Sessions | **Restricted** | **Proceedings** | **Extremely Grave Harm:** Structural breach of legislative integrity and secure proceedings. |
| **S-016** | Audit and Review Findings | **Confidential** | **Audit** | **Serious Harm:** Material damage to trust or disclosure of sensitive compliance investigations. |
| **S-019** | Network Diagrams and Plans | **Confidential** | **Security** | **Serious Harm:** Technical blueprints that facilitate perimeter reconnaissance or cyber threats. |

---

## 2. Automated Labelling & Protection Rules
To enforce uniform compliance without relying solely on manual end-user action, the following auto-labelling conditions are to be configured within the Purview compliance engine:

### Rule A: Immediate Escalation to Restricted (Condition-Driven)
*   **Trigger Conditions:** 
    *   System discovers keywords indicating legal privilege (`"in camera"`, `"legal opinion"`, `"solicitor-client"`).
    *   Content resides within specific executive file directories or senior leadership libraries.
*   **Enforced Actions:** Auto-applies **Restricted — Legal** or **Restricted — Proceedings**. Enforces full file encryption, blocks all external sharing, applies user-specific identity watermarking, and strips printing/forwarding/copying rights completely.

### Rule B: Confidential Tier Profiling (Pattern-Driven)
*   **Trigger Conditions:**
    *   Discovery of highly sensitive personal identifiers (e.g., 1 or more Social Insurance Numbers or Credit Cards).
    *   Discovery of corporate secrets, such as hardcoded passwords, `APIKey_Secret` patterns, or unencrypted database connection string signatures.
    *   Matching structural data fingerprints like `BudgetPattern` syntax or standard invoice/financial layouts.
*   **Enforced Actions:** Auto-applies **Confidential** (paired with *People*, *Financial*, *Commercial*, or *Security* descriptors). Files are dynamically encrypted in-place, headers/watermarks are rendered, and anonymous data links are instantly deactivated.

---

## 3. Microsoft 365 Copilot Scoping Configuration
AI assistant tools dramatically increase data discoverability. To prevent unauthorized extraction of private or sensitive information, the rollout must follow a zero-trust model:

1.  **Restricted Data Exclusion:** Microsoft 365 Copilot is completely prohibited from parsing, indexing, or referencing any asset labeled **Restricted**. This rule applies globally across the tenant—even if the user prompting the AI has native permission to open the source document. This prevents protected legal text or closed-session details from escaping tracking controls through AI-generated summaries.
2.  **Confidential Label Inheritance:** For **Confidential** data, Copilot may process information *only if* the calling user possesses explicit, direct permission to access the underlying file. Any output generated by Copilot from a Confidential source automatically inherits the identical parent label and encryption parameters, preventing it from being leaked to external environments.
3.  **Clean Public/Internal Baseline:** Copilot is permitted to scan **Public** and **Internal** documentation freely for users with an authenticated Assembly account, facilitating rapid summary generation for routine project plans, training guides, and transcripts.

---

## 4. Go-Live Action Plan

To establish these security baselines prior to launching the environment, the following engineering steps must be executed:

*   Step 1: Emergency Link Revocation : 
    Scan `sharing_links_2.csv` and systematically terminate all active `anonymous` links pointing to sites designated as *Internal*, *Confidential*, or *Restricted* (specifically targeting the Legal Opinions Library S-006 and Network Diagrams S-019).
*   Step 2: Schema Standardization : 
    Deploy ETL transformation logic against `site_inventory_3.csv` to resolve duplicate records, enforce uniform lower-case strings, and map dirty or missing labels directly into the validated 4-tier taxonomy.
*   Step 3: Enable Automated Compliance Policies : 
    Publish the auto-labelling rules into production, apply the mandatory Copilot blocklist against the *Restricted* classification, and run a final test cycle with a controlled pilot group before full tenant onboarding.
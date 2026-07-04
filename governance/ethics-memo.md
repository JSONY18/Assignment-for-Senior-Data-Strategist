# EXECUTIVE BRIEF: PRIVACY & ETHICS MEMORANDUM

---

### 1. Executive Summary
A comprehensive scan of our data environment has revealed significant data quality failures and schema issues, structural logic contradictions, critical security vulnerabilities, and privacy data governance and risk exposure. This data state exposes the Legislative Assembly to severe regulatory, financial, and ethical liabilities. Immediate operational intervention is required to stop data leakage and secure high-risk personal data.

---

### 2. Critical Privacy & Ethical Exposures

#### A. Unprotected Sensitive PII Exposure
* **Privacy Exposures & Data Spill:** Over 3,300 instances of unclassified legacy PII bundles, alongside hundreds of SIN scattered across unprotected benefits enrollment, payroll master files, and Legacy Archives.
* **Ethical/Privacy Impact:** Exposing SINs creates high risks for identity information leakage and financial fraud, failing to fulfill our duty of care to employees and constituents.
* **Critical Operational Vulnerabilities:** Hardcoded operational secrets (`APIKey_Secret`) are exposed in IT Security Runbooks, completely undermining our perimeter defenses.

#### B. Unauthorized Data Exposure via Anonymous Sharing
* **High-Risk & Logical Contradictions:** Network Diagrams and Plans and Legal Opinions Library have active, open-ended **Anonymous Sharing Links** enabled. Furthermore, some structural logical contradiction "anonymous" links targeted specifically at an external domain—indicating critical user confusion that threatens solicitor-client privilege.
* **Severe Data Corruption & Fragmentation:** Data integrity is heavily compromised by duplicate infrastructure tracking keys, fragmented/loose department string taxonomies, messy date formats, and character encoding corruption.

---

### 3. Proposed Framework: Label Configuration & Copilot Scoping
We must enforce a strict, unified four-type data classification system across the entire workspace:

| Sensitivity Label | Assembly Descriptor & Policy Mandate |
| :--- | :--- |
| **Public** | Approved for external publication (e.g., official media releases) Zero restriction. |
| **Internal** | Standard legislative operations. No anonymous sharing allowed. |
| **Confidential** | Sensitive human resources, procurement, or operational records. Restricted to specific internal groups or verified partners. |
| **Restricted** | Legal opinions, active incident response, or closed cabinet briefings. Full encryption; absolute ban on external/anonymous sharing. |

#### Proposed Auto-Labelling Rules
* **Rule 1 (Restricted):** Automatically apply if any document matches patterns for `SIN`, `CreditCard`, `APIKey_Secret`, or keywords like `"in camera"`, `"privileged"`.
* **Rule 2 (Confidential):** Automatically apply if a document matches `BudgetPattern` or is saved within HR, Finance, or Audit directories.
* **Rule 3 (Block Anonymous):** Instantly revoke and block anonymous link generation on any asset tagged *Internal*, *Confidential*, or *Restricted*.

#### Copilot Scoping Rule
* Completely exclude the *Restricted* tier from the Copilot index.
* Restrict Copilot access to *Confidential* tiers strictly using Group-Based Access Control, ensuring users can only query data matching their exact HR-verified department.
---

### 4. Immediate Action Plan

#### A. Structural Remediation
* Ingest automated data cleansing script to fix duplicate sites and messy department headers.
* Deploy the standardized 4-tier sensitivity label framework across the entire cloud tenant.

#### B. Secure Rollout
* Run automated compliance scanning rules for PII/Secrets across legacy and active shares.
* Enable Copilot onboarding for internal operational groups.
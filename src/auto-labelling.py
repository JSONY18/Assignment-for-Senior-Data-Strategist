import os
import re

def auto_classify_document(file_path):
    """
    Automates document labeling using the Legislative Assembly framework rules.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    # 1. RESTRICTED RULE: High-harm context keywords
    if "in camera" in content or "do not forward" in content or "privileged" in content:
        if any(kw in content for kw in ["committee", "proceedings", "leadership", "meeting"]):
            return "Restricted — Proceedings"
        elif "legal" in content or "counsel" in content:
            return "Restricted — Legal"
        return "Restricted"
        
    # 2. CONFIDENTIAL RULE: Serious harm patterns (Audit, Finance, Commercial, People)
    if any(kw in content for kw in ["audit", "review findings", "investigation"]):
        return "Confidential — Audit"
    if any(kw in content for kw in ["procurement", "vendor contract", "bid evaluation"]):
        return "Confidential — Commercial"
    if any(kw in content for kw in ["budget", "invoice", "financial results", "expense claim"]):
        return "Confidential — Financial"
    if any(kw in content for kw in ["sin", "employee records", "hiring records", "salary"]):
        return "Confidential — People"
        
    # 3. PUBLIC RULE: External-facing verification
    if "approved for release" in content or "public assembly website" in content:
        return "Public"
        
    # 4. DEFAULT COMPLIANCE FALLBACK
    return "Internal"

# Batch execution example
docs_directory = "data/sample_documents"
for file_name in os.listdir(docs_directory):
    file_path = os.path.join(docs_directory, file_name)
    if os.path.isfile(file_path):
        assigned_label = auto_classify_document(file_path)
        print(f"File: {file_name:<30} -> Assigned Label: {assigned_label}")
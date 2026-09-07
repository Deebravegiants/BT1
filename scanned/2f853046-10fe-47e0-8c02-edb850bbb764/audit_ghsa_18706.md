# [C] bagisto has CSV Formula Injection in Create New Product

## Summary
Severity: Critical
Advisory: GHSA-jqrp-58fv-w8cq
CVE: CVE-2025-62417
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-jqrp-58fv-w8cq
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.8

## Details
### Summary
When product data that begins with a spreadsheet formula character (for example =, +, -, or @) is accepted and later exported or saved into a CSV and opened in spreadsheet software, the spreadsheet will interpret that cell as a formula. This allows an attacker to supply a CSV field (e.g., product name) that contains a formula which may be evaluated by a victim’s spreadsheet application — potentially leading to data exfiltration and remote command execution (via older Excel exploits / OLE/cmd constructs or Excel macros).

### Details
Spreadsheet applications treat cell text that begins with characters =, +, -, @ as formulas. If unescaped, spreadsheet will interpret and evaluate the content when the file is opened. The application fails to neutralize/escape leading formula characters when generating CSV or when accepting CSV import fields for display/export.

### PoC
Insert CSV formula to the product name field, and save the changes. Export it to CSV file, open it and the calc.exe will be executed. Other CSV export functions are affected as well.
http://127.0.0.1/admin/catalog/products/edit/1
<img width="408" height="302" alt="image" src="https://github.com/user-attachments/assets/2c6fd1e3-6725-4bf4-9c64-20cd57f4e279" />
<img width="1696" height="854" alt="image" src="https://github.com/user-attachments/assets/911a69ae-65ac-4a8a-ad8e-63571a9610c8" />

### Impact
Data exfiltration: Using spreadsheet functions (e.g., WEBSERVICE, HYPERLINK, or concatenation to create requests) on victims' machines that make network calls.
Remote command execution: In some historical cases, specially crafted formulas and older Excel behaviors can lead to RCE. Modern Excel hardens many of these, but risk remains depending on environment.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-jqrp-58fv-w8cq
- https://github.com/bagisto/bagisto/commit/8076c708498a0187bc952d5f5f705e0cb1919682
- https://github.com/bagisto/bagisto

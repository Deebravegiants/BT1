# [M] REDAXO CMS is vulnerable to XSS through its module management component

## Summary
Severity: Medium
Advisory: GHSA-vqc7-7fj4-3fm3
CVE: CVE-2025-64049
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-vqc7-7fj4-3fm3
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=0 <5.20.1

## Details
A stored cross-site scripting (XSS) vulnerability in the module management component in REDAXO CMS 5.20.0 allows remote users to inject arbitrary web script or HTML via the Output code field in modules. The payload is executed when a user views or edits an article by adding slice that uses the compromised module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64049
- https://github.com/redaxo/redaxo/commit/58929062312cf03e344ab04067a365e6b6ee66aa
- https://drive.google.com/drive/folders/1SpwL548ZBRYU_uL8W7Riv7VHshr2UN0R?usp=sharing
- https://github.com/redaxo/redaxo
- https://github.com/vettrivel007/CVE-Disclosures/blob/main/CVE-2025-64049.md

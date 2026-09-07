# [M] Subrion CMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vff-rv2f-cj79
CVE: CVE-2023-43884
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-7vff-rv2f-cj79
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
A Cross-site scripting (XSS) vulnerability in Reference ID from the panel Transactions, of Subrion v4.2.1 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into 'Reference ID' parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43884
- https://github.com/dpuenteramirez/XSS-ReferenceID-Subrion_4.2.1
- https://github.com/intelliants/subrion

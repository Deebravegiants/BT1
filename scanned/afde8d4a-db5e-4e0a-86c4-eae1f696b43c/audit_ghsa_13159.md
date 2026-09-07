# [M] Subrion CMS XSS in /panel/configuration/financial/

## Summary
Severity: Medium
Advisory: GHSA-q832-2275-rfqh
CVE: CVE-2023-43830
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-q832-2275-rfqh
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
A Cross-site scripting (XSS) vulnerability in /panel/configuration/financial/ of Subrion v4.2.1 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into several fields: 'Minimum deposit', 'Maximum deposit' and/or 'Maximum balance'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43830
- https://github.com/al3zx/xss_financial_subrion_4.2.1
- https://github.com/intelliants/subrion

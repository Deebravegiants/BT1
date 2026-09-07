# [M] yaffa vulnerable to Cross Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-pq95-94c9-j987
CVE: CVE-2025-70844
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-pq95-94c9-j987
Type: github-advisory

## Affected
- Packagist: `kantorge/yaffa` — affected >=0

## Details
yaffa v2.0.0 is vulnerable to Cross Site Scripting (XSS). An attacker can inject malicious JavaScript into the "Add Account Group" function on the account-group page, allowing execution of arbitrary script in the context of users who view the affected page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70844
- https://github.com/J4cky1028/vulnerability-research/tree/main/CVE-2025-70844
- https://github.com/kantorge/yaffa

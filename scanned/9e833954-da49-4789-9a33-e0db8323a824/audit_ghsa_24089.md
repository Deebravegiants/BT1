# [M] Foxlor cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cv24-vh45-4hjm
CVE: CVE-2020-28957
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cv24-vh45-4hjm
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected 0.10.16

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the Customer Add module of Foxlor v0.10.16 allows attackers to execute arbitrary web scripts or HTML via a crafted payload entered into the name, firstname, or username input fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28957
- https://github.com/Froxlor/Froxlor
- https://www.vulnerability-lab.com/get_content.php?id=2241

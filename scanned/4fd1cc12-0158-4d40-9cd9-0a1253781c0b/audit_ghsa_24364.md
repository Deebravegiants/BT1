# [M] Gravity Forms stored HTML injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fcj2-rxqc-294c
CVE: CVE-2020-27851
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fcj2-rxqc-294c
Type: github-advisory

## Affected
- Packagist: `wp-premium/gravityforms` — affected >=0 <2.4.21

## Details
Multiple stored HTML injection vulnerabilities in the "poll" and "quiz" features in an additional paid add-on of Rocketgenius Gravity Forms before 2.4.21 allows remote attackers to inject arbitrary HTML code via poll or quiz answers. This code is interpreted by users in a privileged role (Administrator, Editor, etc.).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27851
- https://github.com/wp-premium/gravityforms
- https://www.digital.security/advisories/cert-ds_advisory_cve-2020-27851.txt

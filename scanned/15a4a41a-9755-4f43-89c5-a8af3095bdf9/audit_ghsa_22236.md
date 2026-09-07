# [M] Stored XSS in LavaLite 5.2.4

## Summary
Severity: Medium
Advisory: GHSA-h7vh-6gmm-g7h9
CVE: CVE-2017-1000467
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h7vh-6gmm-g7h9
Type: github-advisory

## Affected
- Packagist: `lavalite/cms` — affected >=0

## Details
LavaLite version 5.2.4 is vulnerable to stored cross-site scripting vulnerability, within the blog creation page, which can result in disruption of service and execution of javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000467
- https://github.com/LavaLite/cms/issues/209

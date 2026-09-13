# [M] Concrete CMS is subject to Insecure Direct Object Reference (IDOR) in the Express Entry Detail block

## Summary
Severity: Medium
Advisory: GHSA-chfm-cm6h-q5x7
CVE: CVE-2026-7881
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-chfm-cm6h-q5x7
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is subject to Insecure Direct Object Reference (IDOR) in the Express Entry Detail block via the exEntryID parameter. This IDOR leads to unauthorized access to all Express form submissions. The Concrete CMS security team thanks Tristan Madani for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7881
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms

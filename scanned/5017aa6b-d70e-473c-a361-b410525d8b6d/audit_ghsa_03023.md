# [M] Password exposure in concrete5/core

## Summary
Severity: Medium
Advisory: GHSA-rhf5-f553-xg82
CVE: CVE-2021-22951
CWE: CWE-200, CWE-639
Ecosystem: Packagist
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-rhf5-f553-xg82
Type: github-advisory

## Affected
- Packagist: `concrete5/core` — affected >=0 <8.5.7

## Details
Unauthorized individuals could view password protected files using view_inline in Concrete CMS (previously concrete 5) prior to version 8.5.7. Concrete CMS now checks to see if a file has a password in view_inline and, if it does, the file is not rendered.For version 8.5.6, the following mitigations were put in place a. restricting file types for view_inline to images only b. putting a warning in the file manager to advise users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22951
- https://hackerone.com/reports/1102014
- https://documentation.concretecms.org/developers/introduction/version-history/857-release-notes

# [M] Exposure of sensitive information in concrete5/core

## Summary
Severity: Medium
Advisory: GHSA-m2v2-8227-59f5
CVE: CVE-2021-22967
CWE: CWE-200, CWE-639
Ecosystem: Packagist
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-m2v2-8227-59f5
Type: github-advisory

## Affected
- Packagist: `concrete5/core` — affected >=0 <8.5.7

## Details
In Concrete CMS (formerly concrete 5) below 8.5.7, IDOR Allows Unauthenticated User to Access Restricted Files If Allowed to Add Message to a Conversation.To remediate this, a check was added to verify a user has permissions to view files before attaching the files to a message in "add / edit message”.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22967
- https://hackerone.com/reports/869612
- https://documentation.concretecms.org/developers/introduction/version-history/857-release-notes

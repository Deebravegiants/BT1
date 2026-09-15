# [M] NocoDB vulnerable to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-grv6-m753-3w2g
CVE: CVE-2022-3423
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-grv6-m753-3w2g
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.92.0

## Details
NocoDB prior to 0.92.0 allows actors to insert large characters into the input field `New Project` on the create field, which can cause a Denial of Service (DoS) via a crafted HTTP request. Version 0.92.0 fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3423
- https://github.com/nocodb/nocodb/commit/000ecd886738b965b5997cd905825e3244f48b95
- https://github.com/nocodb/nocodb
- https://huntr.dev/bounties/94639d8e-8301-4432-ab80-e76e1346e631

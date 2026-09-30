# [C] Exposure of Resource to Wrong Sphere in org.craftercms:crafter-search

## Summary
Severity: Critical
Advisory: GHSA-2wr2-8qjq-gh55
CVE: CVE-2021-23264
CWE: CWE-402, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-2wr2-8qjq-gh55
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-search` — affected >=3.1.0 <3.1.15

## Details
Installations, where crafter-search is not protected, allow unauthenticated remote attackers to create, view, and delete search indexes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23264
- https://github.com/craftercms/craftercms/commit/0e256ef0372c7be9d6e2fefc4652dd4fd94770a1
- https://docs.craftercms.org/en/3.1/security/advisory.html#cv-2021120107

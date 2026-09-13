# [M] Missing Authorization in Crafter CMS

## Summary
Severity: Medium
Advisory: GHSA-2rr8-9c6g-8j5c
CVE: CVE-2017-15680
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2rr8-9c6g-8j5c
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-core` — affected >=3.0.0 <3.0.1

## Details
In Crafter CMS Crafter Studio 3.0 prior to 3.0.1 an IDOR vulnerability exists which allows unauthenticated attackers to view and modify administrative data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15680
- https://docs.craftercms.org/en/3.0/security/advisory.html

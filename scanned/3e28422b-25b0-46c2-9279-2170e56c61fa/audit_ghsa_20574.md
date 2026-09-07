# [M] SQL Injection in showdoc

## Summary
Severity: Medium
Advisory: GHSA-9cq5-xgg4-x477
CVE: CVE-2022-0362
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-9cq5-xgg4-x477
Type: github-advisory

## Affected
- Packagist: `showdoc/showdoc` — affected >=0 <2.10.3

## Details
Showdoc verions 2.10.2 and prior is vulnerable to SQL injection. A patch is available in the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0362
- https://github.com/star7th/showdoc/commit/2b34e267e4186125f99bfa420140634ad45801fb
- https://github.com/star7th/showdoc
- https://huntr.dev/bounties/e7c72417-eb8f-416c-8480-be76ac0a9091

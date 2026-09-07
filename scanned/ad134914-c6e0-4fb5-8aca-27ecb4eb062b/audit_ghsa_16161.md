# [M] CSRF leading to delete account in wallabag/wallabag

## Summary
Severity: Medium
Advisory: GHSA-99w8-c5f6-96pp
CVE: CVE-2023-0737
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-99w8-c5f6-96pp
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=0 <2.5.4

## Details
wallabag version 2.5.2 contains a Cross-Site Request Forgery (CSRF) vulnerability that allows attackers to arbitrarily delete user accounts via the /account/delete endpoint. This issue is fixed in version 2.5.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0737
- https://github.com/wallabag/wallabag/commit/268372dbbdd7ef87b84617fdebf95d0a86caf7dc
- https://github.com/wallabag/wallabag
- https://huntr.com/bounties/4ba20fe7-4061-4dfb-ab2f-ecaf110641a5

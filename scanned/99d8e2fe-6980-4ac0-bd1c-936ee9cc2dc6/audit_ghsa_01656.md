# [H] Private data exposure via REST API in BuddyPress

## Summary
Severity: High
Advisory: GHSA-3j78-7m59-r7gv
CVE: CVE-2020-5244
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-3j78-7m59-r7gv
Type: github-advisory

## Affected
- Packagist: `buddypress/buddypress` — affected >=0 <5.1.2

## Details
In BuddyPress before 5.1.2, requests to a certain REST API endpoint can result in private user data getting exposed. Authentication is not needed.

This has been patched in version 5.1.2.

## References
- https://github.com/buddypress/BuddyPress/security/advisories/GHSA-3j78-7m59-r7gv
- https://nvd.nist.gov/vuln/detail/CVE-2020-5244
- https://github.com/buddypress/BuddyPress/commit/39294680369a0c992290577a9d740f4a2f2c2ca3
- https://buddypress.org/2020/01/buddypress-5-1-2

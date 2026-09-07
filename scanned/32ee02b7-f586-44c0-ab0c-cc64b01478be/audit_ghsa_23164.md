# [M] BuddyPress Docs plugin Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-9wf6-88x4-6xvj
CVE: CVE-2017-6954
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9wf6-88x4-6xvj
Type: github-advisory

## Affected
- Packagist: `buddypress/buddypress` — affected >=0 <1.9.3

## Details
An issue was discovered in `includes/component.php` in the BuddyPress Docs plugin before 1.9.3 for WordPress. It is possible for authenticated users to edit documents of other users without proper permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6954
- https://github.com/boonebgorges/buddypress-docs/commit/75293ed4e5f31f04e54689bfe2c647e3e3f5e1a9
- https://wordpress.org/plugins/buddypress-docs/changelog
- http://www.securityfocus.com/bid/97238

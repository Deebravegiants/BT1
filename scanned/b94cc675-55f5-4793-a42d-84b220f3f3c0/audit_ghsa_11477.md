# [H] Connect CMS: Improper Authorization in the My Page Profile Update Feature Allows Modification of Arbitrary User Information

## Summary
Severity: High
Advisory: GHSA-qr6x-wvxr-8hm9
CVE: CVE-2026-32300
CWE: CWE-285, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-qr6x-wvxr-8hm9
Type: github-advisory

## Affected
- Packagist: `opensource-workshop/connect-cms` — affected >=0 <1.41.1
- Packagist: `opensource-workshop/connect-cms` — affected >=2.0.0 <2.41.1

## Details
# Security Advisory — My Page Profile Update (Improper Authorization)

## Summary

An improper authorization issue in the My Page profile update feature may allow modification of arbitrary user information.

## Affected Versions

- 1.x series: <= 1.41.0
- 2.x series: <= 2.41.0

## Patched Versions

- 1.41.1
- 2.41.1

## Description

In part of the My Page profile update feature, another user's profile information or password could be modified. If exploited, arbitrary user accounts may be taken over. Exploitation requires that the attacker be able to reach the affected functionality as an authenticated user. Users affected by this vulnerability should update to a fixed version.

## Solution

Update to the fixed version.
For the 1.x series, update to 1.41.1 or later.
For the 2.x series, update to 2.41.1 or later.

## Credits

OpenSource WorkShops thanks **Sho Odagiri** (小田切 祥) of **GMO Cybersecurity by Ierae, Inc.** for reporting this vulnerability.

## References
- https://github.com/opensource-workshop/connect-cms/security/advisories/GHSA-qr6x-wvxr-8hm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32300
- https://github.com/opensource-workshop/connect-cms/commit/7c9951738c62a1d51b91e9956d1eb756c5d52cce
- https://github.com/opensource-workshop/connect-cms
- https://github.com/opensource-workshop/connect-cms/releases/tag/v1.41.1
- https://github.com/opensource-workshop/connect-cms/releases/tag/v2.41.1

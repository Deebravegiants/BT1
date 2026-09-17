# [M] baserCMS Directory Traversal vulnerability in Form submission data management Feature

## Summary
Severity: Medium
Advisory: GHSA-hmqj-gv2m-hq55
CVE: CVE-2023-43648
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-hmqj-gv2m-hq55
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.8.0

## Details
There is a Directory Traversal Vulnerability in Form submission data management Feature to baserCMS.

This is a vulnerability that needs to be addressed when the management system is used by an unspecified number of users.
If you are eligible, please update to the new version as soon as possible.

### Target
baserCMS 4.7.8 and earlier versions

### Vulnerability
There is a possibility that information on the server may be obtained by a user who is logged in to the management screen.

### Countermeasures
Update to the latest version of baserCMS

Please refer to the following page to reference for more information.
https://basercms.net/security/JVN_45547161

### Credits
Shiga Takuma@BroadBand Security, Inc

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-hmqj-gv2m-hq55
- https://nvd.nist.gov/vuln/detail/CVE-2023-43648
- https://github.com/baserproject/basercms/commit/7555a5cf0006755dc0223fffc2d882b50a97758b
- https://basercms.net/security/JVN_81174674
- https://github.com/baserproject/basercms

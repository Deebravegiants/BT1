# [H] Potential Zip Slip Vulnerability in baserCMS

## Summary
Severity: High
Advisory: GHSA-4x2f-54wr-4hjg
CVE: CVE-2021-41279
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-4x2f-54wr-4hjg
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.5.4

## Details
There is a OS Command Injection Vulnerability on the management system of baserCMS.

This is a vulnerability that needs to be addressed when the management system is used by an unspecified number of users.
If you are eligible, please update to the new version as soon as possible.

Target
baserCMS 4.5.3 and earlier versions

Vulnerability
OS Command Injection Vulnerability.

Countermeasures
Update to the latest version of baserCMS

Credits
Daniele Scanu @SoterItSecurity

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-4x2f-54wr-4hjg
- https://nvd.nist.gov/vuln/detail/CVE-2021-41279
- https://github.com/baserproject/basercms/commit/d8ab0a81a7bce35cc95ff7dff851a7e87a084336
- https://github.com/baserproject/basercms

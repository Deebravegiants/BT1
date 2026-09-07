# [M] silverstripe/framework's install.php script discloses sensitive data by pre-populating DB credential forms

## Summary
Severity: Medium
Advisory: GHSA-r3pr-fh25-wrfc
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-r3pr-fh25-wrfc
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.1

## Details
When accessing the `install.php` script it is possible to extract any pre-configured database or default admin account password by viewing the source of the page, and inspecting the `value` property of the password fields.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/7a79cd039a96ef54182263d5fbb72addf093b171
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-010-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-010

# [M] silverstripe/framework may disclose database credentials during connection failure

## Summary
Severity: Medium
Advisory: GHSA-m2hh-2m46-x6j5
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-m2hh-2m46-x6j5
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.7.0-rc1 <3.7.1
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.5
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.3
- Packagist: `silverstripe/framework` — affected >=4.2.0-rc1 <4.2.2

## Details
When running SilverStripe 3.7 or 4.x in dev mode with the mysqli database driver, there is a potential to disclose the connection details.

We have blacklisted the sensitive parts of the connection information from being included in dev mode stack traces when database errors occur.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/214e28127f5425b61c15b69f884afdbad31133c2
- https://github.com/silverstripe/silverstripe-framework/commit/54251952387394d72b221e797a80edfbf9a973ee
- https://github.com/silverstripe/silverstripe-framework/commit/9aabe0a0f7a061d87cc92923f8811e14d7a032f5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-018-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-018

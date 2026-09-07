# [M] silverstripe/framework users inadvertently passing sensitive data to LoginAttempt

## Summary
Severity: Medium
Advisory: GHSA-ph62-fv59-vf9h
CWE: CWE-311
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-ph62-fv59-vf9h
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.6
- Packagist: `silverstripe/framework` — affected >=3.6.0-rc1 <3.6.3
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.1

## Details
All user login attempts are logged in the database in the LoginAttempt table. However, this table contains information in plain text, and may possible contain sensitive information, such as user passwords mis-typed into the username field.

In order to address this a one-way hash is applied to the Email field before being stored.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/3e2bcaa0b49277ff7f7004b265a7fa80d0b92e5c
- https://github.com/silverstripe/silverstripe-framework/commit/c5d6eb816d4ac5e9fa3d8bc4bd82de95719eb22d
- https://github.com/silverstripe/silverstripe-framework/commit/f1dd3d6f03eb1d94c29c495994a1da9176a758d9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-009-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-009

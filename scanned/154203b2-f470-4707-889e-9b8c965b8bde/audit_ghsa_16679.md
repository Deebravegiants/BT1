# [H] silverstripe/subsites Unsafe SQL Query Construction (Safe Data Source)

## Summary
Severity: High
Advisory: GHSA-xc69-p8fc-m6m5
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-xc69-p8fc-m6m5
Type: github-advisory

## Affected
- Packagist: `silverstripe/subsites` — affected >=2.0.0 <2.1.1

## Details
There is a low level potential SQL injection vulnerability in the silverstripe/subsites module has been identified and fixed in version 2.1.1.

## References
- https://github.com/silverstripe/silverstripe-subsites/commit/bf2c81dce62ae9a7623d224fd31a39505260eb57
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/subsites/SS-2018-016-1.yaml
- https://github.com/silverstripe/silverstripe-subsites
- https://www.silverstripe.org/download/security-releases/ss-2018-016

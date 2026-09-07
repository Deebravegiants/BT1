# [H] silverstripe/framework has potential SQL Injection vulnerability in PostgreSQL database connector

## Summary
Severity: High
Advisory: GHSA-265q-222x-52m6
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-265q-222x-52m6
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.6
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.4
- Packagist: `silverstripe/framework` — affected >=4.2.0-rc1 <4.2.3

## Details
A potential SQL injection vulnerability was identified by using the silverstripe/postgresql database adapter. While unlikely to be exploitable, we have patched silverstripe/framework to ensure that table names are safely escaped before being passed to database adapters or user code.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/48bd335648188df9dae72be1e5f9c808f3fe1e77
- https://github.com/silverstripe/silverstripe-framework/commit/fecedc2d98eeaaff6424fb59dc70ef6bdc6dc92d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-020-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-020

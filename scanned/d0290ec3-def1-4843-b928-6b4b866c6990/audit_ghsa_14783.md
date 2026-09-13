# [H] zfr authentication adapter did not verify validity of tokens

## Summary
Severity: High
Advisory: GHSA-rcm4-jv5g-wccm
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-rcm4-jv5g-wccm
Type: github-advisory

## Affected
- Packagist: `zfr/zfr-oauth2-server-module` — affected >=0 <0.1.2

## Details
Previous to @2ca5bb1c2f11537be8f94ca6867d8d69789e744a (release [0.1.2](https://github.com/zf-fr/zfr-oauth2-server-module/tree/0.1.2)), tokens weren't checked for validity/expiration.

This potentially caused a security issue if expired tokens were not deleted after the expiration time was past, allowing anyone to still use invalidated authentication credentials.

## References
- https://github.com/zf-fr/zfr-oauth2-server-module/issues/6
- https://github.com/zf-fr/zfr-oauth2-server-module/commit/2ca5bb1c2f11537be8f94ca6867d8d69789e744a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zfr/zfr-oauth2-server-module/2014-04-26.yaml
- https://github.com/zf-fr/zfr-oauth2-server-module
- https://github.com/zf-fr/zfr-oauth2-server-module/tree/0.1.2

# [H] silverstripe/framework BackURL validation bypass with malformed URLs

## Summary
Severity: High
Advisory: GHSA-m5q3-mvcr-gc5m
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-m5q3-mvcr-gc5m
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
A carefully constructed malformed URL can be used to circumvent the offsite redirection protection used on `BackURL` parameters. This could lead to users entering sensitive data in malicious websites instead of the intended one.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/9053014a7e2eba28d000881e0bb3cc1d6e6b2eea
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-008-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-008

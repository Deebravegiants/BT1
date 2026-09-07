# [H] silverstripe/framework has possible denial of service attack vector when flushing

## Summary
Severity: High
Advisory: GHSA-cwgq-83w5-8jfq
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-cwgq-83w5-8jfq
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.5
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.3
- Packagist: `silverstripe/framework` — affected >=4.2.0-rc1 <4.2.2

## Details
A possible denial of service attack vector has been identified in the dev/build system controller.

dev/build now has its own URL token, similar to flushtoken, to ensure users are authenticated when running dev/build outside of dev environments.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/0610f76da02ac53a1b51cdfe9eac34e943a66991
- https://github.com/silverstripe/silverstripe-framework/commit/8d7c2dafabad505d769f3774c44e0595fb1a4cd9
- https://github.com/silverstripe/silverstripe-framework/commit/af000bea9b16ea553cae7f7f662f74ab8dc343df
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-019-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-019

# [H] silverstripe/framework's User-Agent header not correctly invalidating user session

## Summary
Severity: High
Advisory: GHSA-4qx8-j9vh-2628
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-4qx8-j9vh-2628
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.6
- Packagist: `silverstripe/framework` — affected >=3.6.0-rc1 <3.6.3

## Details
A security protection device in Session designed to protect session hijacking was not correctly functioning. This function intended to protect user sessions by detecting changes in the User-Agent header, but modifications to this header were not correctly invalidating the user session.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/44de03da0147e6094b02602b7b73d5b1a1306d78
- https://github.com/silverstripe/silverstripe-framework/commit/d47667bb0768841e4b305fa95d5a4e2ba232c4ad
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-006-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-006

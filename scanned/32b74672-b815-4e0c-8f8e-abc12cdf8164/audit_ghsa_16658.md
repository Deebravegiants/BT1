# [M] Silverstripe Cross-site scripting vulnerability in VersionedRequestFilter

## Summary
Severity: Medium
Advisory: GHSA-mpqj-f4v3-334h
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-mpqj-f4v3-334h
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.3.2 <3.3.3
- Packagist: `silverstripe/framework` — affected >=3.4.0 <3.4.1

## Details
A cross-site scripting vulnerability in VersionedRequestFilter has been found.

If an incoming user request should not be able to access the requested stage, an error message is created for display on the CMS login page that they are redirected to. In this error message, the URL of the requested page is interpolated into the error message without being escaped; hence, arbitrary HTML can be injected into the CMS login page.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/3fa84cf0c64a539d78600c36364817a8e38411d8
- https://github.com/silverstripe/silverstripe-framework/commit/41be95c95a55031412ee4056aeee5c2c69595836
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-007-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-007

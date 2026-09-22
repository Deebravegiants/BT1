# [M] endroid/qr-code-bundle File Disclosure via logo_path query parameter

## Summary
Severity: Medium
Advisory: GHSA-mvf6-3f2g-xfxf
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-mvf6-3f2g-xfxf
Type: github-advisory

## Affected
- Packagist: `endroid/qr-code-bundle` — affected >=0 <3.4.2

## Details
Versions of endroid/qr-code-bundle prior to 3.4.2 are affected by a security vulnerability that allows disclosure of files through the logo_path query parameter. The vulnerability arises from the improper handling of non-image data as the logo, which could lead to unintended file disclosure.

## References
- https://github.com/endroid/qr-code-bundle/commit/51928eaaa30e7db1fd3f1076744dcbc8f8cec8c8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/endroid/qr-code-bundle/2019-12-22.yaml
- https://github.com/endroid/qr-code-bundle
- https://github.com/endroid/qr-code-bundle/releases/tag/3.4.2

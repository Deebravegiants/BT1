# [H] silverstripe/framework code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-vgxh-x8jv-hmff
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-vgxh-x8jv-hmff
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.3-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
There is a vulnerability whereby arbitrary global functions may be executed if malicious user input is passed through to in the second argument of `ViewableData::renderWith`. This argument resolves associative arrays as template placeholders. This exploit requires that user code has been written which makes use of the second argument in `renderWith` and where user input is passed directly as a value in an associative array without sanitisation such as `Convert::raw2xml()`.

`ViewableData::customise` is not vulnerable.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/6f50728b185e62c0087a58b295a015cb13276911
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-006-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-006

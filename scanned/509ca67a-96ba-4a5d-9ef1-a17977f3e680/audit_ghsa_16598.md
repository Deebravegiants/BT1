# [M] silverstripe/framework vulnerable to Cross-site Scripting In `OptionsetField` and `CheckboxSetField`

## Summary
Severity: Medium
Advisory: GHSA-468j-6jrc-2rjx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-468j-6jrc-2rjx
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.19-rc1 <3.1.20
- Packagist: `silverstripe/framework` — affected >=3.2.4-rc1 <3.2.5
- Packagist: `silverstripe/framework` — affected >=3.3.2-rc1 <3.3.3
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.1

## Details
List of key / value pairs assigned to `OptionsetField` or `CheckboxSetField` do not have a default casting assigned to them. The effect of this is a potential XSS vulnerability in lists where either key or value contain unescaped HTML.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/049cdefacfd3122d59d5488c1317f999fe8aacc4
- https://github.com/silverstripe/silverstripe-framework/commit/12a6b357e761f09d818fd0013eb2d85014de79a0
- https://github.com/silverstripe/silverstripe-framework/commit/62a242154ec3508fe9b174a40713c8520ac1684c
- https://github.com/silverstripe/silverstripe-framework/commit/b0ba2015d9684ee7b124dafcf6b59b046e20f8ed
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-015-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-015

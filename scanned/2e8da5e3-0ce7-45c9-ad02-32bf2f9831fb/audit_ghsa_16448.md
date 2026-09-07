# [H] silverstripe/framework CSV Excel Macro Injection

## Summary
Severity: High
Advisory: GHSA-mqjc-x563-c9q8
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-mqjc-x563-c9q8
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.6
- Packagist: `silverstripe/framework` — affected >=3.6.0-rc1 <3.6.3
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.1

## Details
In the CSV export feature of the CMS it's possible for the output to contain macros and scripts, which if imported without sanitisation into software (including Microsoft Excel) may be executed.

In order to safeguard against this threat all potentially executable cell values exported from CSV will be prepended with a literal tab character.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/55739fa5af6171594b2cb4f3621d5fcce5e887d4
- https://github.com/silverstripe/silverstripe-framework/commit/cfe1d4f481bf53ea8da2b8608a563e207d923df9
- https://github.com/silverstripe/silverstripe-framework/commit/dd4c5417e7592e29e698af428b72bdb9b6729797
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-007-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-007

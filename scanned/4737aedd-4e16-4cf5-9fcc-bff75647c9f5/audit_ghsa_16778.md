# [M] Silverstripe Form field validation message XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j982-5jv7-v43r
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-j982-5jv7-v43r
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <3.1.16
- Packagist: `silverstripe/framework` — affected >=3.2.0 <3.2.1

## Details
A high level XSS risk has been identified in the encoding of validation messages in certain FormField classes.

Certain fields such as the NumericField and DropdownField have been identified, but any form field which presents any invalid content as a part of its validation response will be at risk.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/245e0aae2f5f3eb0acba1d198ad8e196bb224462
- https://github.com/silverstripe/silverstripe-framework/commit/bc1b2893accba6401c03f9ea3b0cbc4621c7a02c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-026-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2015-026

# [M] Silverstripe XSS in TreeDropdownField and TreeMultiSelectField

## Summary
Severity: Medium
Advisory: GHSA-r32j-mr8p-hfp8
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-r32j-mr8p-hfp8
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.10

## Details
A cross-site scripting vulnerability has been discovered in the TreeDropdownField and TreeMultiSelectField.

This vulnerability can only be exploited if a user with CMS access has posted malicious or unescaped HTML into any of the dataobjects used as a data source for either of these fields.

This has been resolved by ensuring that all dataobjects used as a data source have their content safely encoded.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/89c14d079d3a130d6c4029af596262528ce53925
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-004-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-004

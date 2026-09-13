# [H] robrichards/xmlseclibs XPath injection

## Summary
Severity: High
Advisory: GHSA-2g98-f9jv-w8c5
CWE: CWE-91
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-2g98-f9jv-w8c5
Type: github-advisory

## Affected
- Packagist: `robrichards/xmlseclibs` — affected >=1.0.0 <3.0.2

## Details
A vulnerability has been identified in the robrichards/xmlseclibs library, specifically related to XPath injection. The issue arises from inadequate filtering of user input before it is incorporated into XPath expressions.

## References
- https://github.com/robrichards/xmlseclibs/commit/649032643f7aac493e91ca318da0339aec72aa4a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/robrichards/xmlseclibs/2018-09-27.yaml
- https://github.com/robrichards/xmlseclibs

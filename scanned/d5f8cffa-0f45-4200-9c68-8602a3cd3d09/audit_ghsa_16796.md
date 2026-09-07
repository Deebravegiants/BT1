# [M] Silverstripe XSS in dev/build returnURL Parameter

## Summary
Severity: Medium
Advisory: GHSA-hq4p-5mpr-jj9m
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-hq4p-5mpr-jj9m
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.14

## Details
A XSS risk exists in the returnURL parameter passed to dev/build. An unvalidated url could cause the user to redirect to an unverified third party url outside of the site.

This issue is resolved in framework 3.1.14 stable release.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/751d77386c3c6e354b521fa61ff142f95895cca8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-015-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-015

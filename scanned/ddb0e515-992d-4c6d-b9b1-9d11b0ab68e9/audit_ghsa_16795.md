# [M] Silverstripe XSS in CMS Edit Page

## Summary
Severity: Medium
Advisory: GHSA-m8v7-x398-pxrf
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-m8v7-x398-pxrf
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.18 <3.1.19
- Packagist: `silverstripe/framework` — affected >=3.2.3 <3.2.4
- Packagist: `silverstripe/framework` — affected >=3.3.1 <3.3.2

## Details
Due to a lack of parameter sanitisation a carefully crafted URL could be used to inject arbitrary HTML into the CMS Edit page.

An attacker could create a URL and share it with a site administrator to perform an attack.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/a24c8260b1d048dc6a0836eb1be9a1ca2056e770
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-004-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://github.com/silverstripe/silverstripe-framework/commits/3.3.2
- https://www.silverstripe.org/download/security-releases/ss-2016-004

# [M] SilverStripe framework XML Quadratic Blowup Attack

## Summary
Severity: Medium
Advisory: GHSA-g43w-98wp-m694
CWE: CWE-400, CWE-776
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-g43w-98wp-m694
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.12

## Details
A low level vulnerability has been found in the SilverStripe framework, where the Quadratic Blowup Attack could potentially be exploited to affect the performance of a site.

See http://mashable.com/2014/08/06/wordpress-xml-blowup-dos/ for a writeup.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/7f983c2bae1dc78ca7217e9af364b2fb71dcefe8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2014-017-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2014-017-xml-quadratic-blowup-attack

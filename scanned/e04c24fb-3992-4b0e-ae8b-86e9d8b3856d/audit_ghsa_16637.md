# [M] Silverstripe XSS In rewritten hash links

## Summary
Severity: Medium
Advisory: GHSA-34q6-xqxh-gq39
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-34q6-xqxh-gq39
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.0.13
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.12

## Details
A high level XSS vulnerability has been discovered in the SilverStripe framework which causes links containing hash anchors (E.g. href="#anchor") to be rewritten in an unsafe way.

The rewriteHashlinks option on SSViewer will rewrite these to contain the current url, although without adequate escaping, meaning that HTML could be injected via injecting unsafe values to any page via the querystring.

Due to the nature of this issue it is likely that a large number of SilverStripe sites are affected.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/604c32871202064a4aa12c3b3fd58140231685e5
- https://github.com/silverstripe/silverstripe-framework/commit/bdef4fc7a548c7c243ff86f2db7c16f301a6f120
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-009-1.yaml
- https://www.silverstripe.org/software/download/security-releases/ss-2015-009-xss-in-rewritten-hash-links
- silverstripe/silverstripe-framework

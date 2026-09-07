# [M] Silverstripe IE requests not properly behaving with rewritehashlinks

## Summary
Severity: Medium
Advisory: GHSA-5f5v-5c3v-gw5v
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-5f5v-5c3v-gw5v
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.0.13
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.12

## Details
Non IE browsers don’t appear to be affected, but I haven’t tested a wide range of browsers to be sure 

Requests that come through from IE do NOT appear to encode all entities in the URL string, meaning they are inserted into output content directly by SSViewer::process() when rewriting hashlinks, as it directly outputs $_SERVER[‘REQUEST_URI’]

**Example IE8 request**
127.0.0.1 - - [18/Jun/2014:14:13:42 +1000] “GET /site/cars/brands/toyota?one=1\”onmouseover=\”alert(‘things’);\” HTTP/1.1” 200

**Example FF request**
127.0.0.1 - - [18/Jun/2014:14:14:22 +1000] “GET /site/cars/brands/toyota?one=1\%22onmouseover=\%22alert(%27things%27);\%22 HTTP/1.1” 200

This causes any hash anchor to have the JS code inserted into the page as-is.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/604c32871202064a4aa12c3b3fd58140231685e5
- https://github.com/silverstripe/silverstripe-framework/commit/bdef4fc7a548c7c243ff86f2db7c16f301a6f120
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2014-015-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2014-015-ie-requests-not-properly-behaving-with-rewritehashlinks

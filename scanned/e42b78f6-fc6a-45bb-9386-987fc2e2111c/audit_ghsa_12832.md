# [H] CakePHP vulnerable to Denial of Service attack through XML payloads

## Summary
Severity: High
Advisory: GHSA-q79m-c546-2g63
Ecosystem: Packagist
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-q79m-c546-2g63
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=3.0.0 <3.0.6
- Packagist: `cakephp/cakephp` — affected >=2.0.0 <2.0.99
- Packagist: `cakephp/cakephp` — affected >=2.1.0 <2.1.99
- Packagist: `cakephp/cakephp` — affected >=2.2.0 <2.2.99
- Packagist: `cakephp/cakephp` — affected >=2.3.0 <2.3.99
- Packagist: `cakephp/cakephp` — affected >=2.4.0 <2.4.99
- Packagist: `cakephp/cakephp` — affected >=2.5.0 <2.5.90
- Packagist: `cakephp/cakephp` — affected >=2.6.0 <2.6.6

## Details
RequestHandlerComponent had a vulnerability that would allow well crafted requests to create a denial of service attack. RequestHandlerComponent leverages `Xml::build()` which allows reading local files. We recommend that all applications using RequestHandlerComponent upgrade, or disable parsing XML payloads.

## References
- https://github.com/cakephp/cakephp/commit/c186487151356a8d7c6e2cae05f87b9df0e59fbb
- https://bakery.cakephp.org/2015/05/28/cakephp_2_6_6_and_3_0_6_released.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cakephp/cakephp/2015-05-28.yaml
- https://github.com/cakephp/cakephp

# [M] CakePHP SecurityComponent cross form submission issue

## Summary
Severity: Medium
Advisory: GHSA-j9q2-f9q7-jhgq
Ecosystem: Packagist
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-j9q2-f9q7-jhgq
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=2.0.0 <2.4.8
- Packagist: `cakephp/cakephp` — affected >=1.3.0 <1.3.18

## Details
Prior to versions 2.4.8 and 1.3.18, forms secured by SecurityComponent could be submitted to any action without triggering SecurityComponent’s tampering protection. If an application contained multiple POST forms to manipulate the same models, it could be vulnerable to mass assignment issues.

## References
- https://github.com/cakephp/cakephp/commit/f23d811ff59c50ef278e98bb75f4ec1e7e54a5b3
- https://bakery.cakephp.org/2014/04/29/CakePHP-1-3-18-and-2-4-8-released.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cakephp/cakephp/2014-04-29.yaml
- https://github.com/cakephp/cakephp

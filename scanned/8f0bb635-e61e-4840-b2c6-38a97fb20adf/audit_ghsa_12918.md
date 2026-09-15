# [M] CakePHP vulnerable to Remote File Inclusion through View template name manipulation

## Summary
Severity: Medium
Advisory: GHSA-p76f-wr22-4rv6
Ecosystem: Packagist
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-p76f-wr22-4rv6
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=2.0.0 <2.0.99
- Packagist: `cakephp/cakephp` — affected >=2.1.0 <2.1.99
- Packagist: `cakephp/cakephp` — affected >=2.2.0 <2.2.99
- Packagist: `cakephp/cakephp` — affected >=2.3.0 <2.3.99
- Packagist: `cakephp/cakephp` — affected >=2.4.0 <2.4.99
- Packagist: `cakephp/cakephp` — affected >=2.5.0 <2.5.99
- Packagist: `cakephp/cakephp` — affected >=2.6.0 <2.6.12
- Packagist: `cakephp/cakephp` — affected >=2.7.0 <2.7.6
- Packagist: `cakephp/cakephp` — affected >=3.0.0 <3.0.15
- Packagist: `cakephp/cakephp` — affected >=3.1.0 <3.1.4

## Details
CakePHP 2.x prior to 2.0.99, 2.1.99, 2.2.99, 2.3.99, 2.4.99, 2.5.99, 2.6.12, and 2.7.6 and 3.x prior to 3.0.15 and 3.1.4 is vulnerable to Remote File Inclusion through View template name manipulation.

## References
- https://github.com/cakephp/cakephp/commit/5e60cc5d182e6131e3fbdfdf69f49d560c9ff78b
- https://bakery.cakephp.org/2015/11/05/cakephp_3015_314_2612_276_released.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cakephp/cakephp/2015-11-05.yaml
- https://github.com/cakephp/cakephp

# [M] ZendFramework1 Potential Security Issues in Bundled Dojo Library

## Summary
Severity: Medium
Advisory: GHSA-w5mj-j45q-m638
Ecosystem: Packagist
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-w5mj-j45q-m638
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.9.0 <1.9.8
- Packagist: `zendframework/zendframework1` — affected >=1.10.0 <1.10.3

## Details
In mid-March, 2010, the Dojo Foundation issued a Security Advisory indicating potential security issues with specific files in Dojo Toolkit. Details of the advisory may be found on the Dojo website:

http://dojotoolkit.org/blog/post/dylan/2010/03/dojo-security-advisory/
In particular, several files in the Dojo tree were identified as having potential exploits, and the Dojo team also advised disabling or removing any PHP scripts in the tree when deploying to production.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2010-07.yaml
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20210509072723/https://framework.zend.com/security/advisory/ZF2010-07
- http://dojotoolkit.org/blog/post/dylan/2010/03/dojo-security-advisory

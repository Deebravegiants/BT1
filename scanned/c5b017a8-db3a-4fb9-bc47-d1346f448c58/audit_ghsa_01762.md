# [M] Exceptions displayed in non-debug configurations in Symfony

## Summary
Severity: Medium
Advisory: GHSA-m884-279h-32v2
CVE: CVE-2020-5274
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2020-03-30
Source: https://github.com/advisories/GHSA-m884-279h-32v2
Type: github-advisory

## Affected
- Packagist: `symfony/error-handler` — affected >=4.4.0 <4.4.4
- Packagist: `symfony/error-handler` — affected >=5.0.0 <5.0.4
- Packagist: `symfony/symfony` — affected >=4.4.0 <4.4.4
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.0.4

## Details
Description
-----------

When `ErrorHandler` renders an exception HTML page, it uses un-escaped properties from the related Exception class to render the stacktrace. The security issue comes from the fact that the stacktraces were also displayed in non-`debug` environments.

Resolution
----------

The `ErrorHandler` class now escapes all properties coming from the related Exception, and the stacktrace is not displayed anymore in non-`debug` environments.

The patches for this issue are available [here](https://github.com/symfony/symfony/commit/cf80224589ac05402d4f72f5ddf80900ec94d5ad) and [here](https://github.com/symfony/symfony/commit/629d21b800a15dc649fb0ae9ed7cd9211e7e45db) for branch 4.4.

Credits
-------

I would like to thank Luka Sikic for reporting & Yonel Ceruto and Jérémy Derussé for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-m884-279h-32v2
- https://nvd.nist.gov/vuln/detail/CVE-2020-5274
- https://github.com/symfony/symfony/commit/629d21b800a15dc649fb0ae9ed7cd9211e7e45db
- https://github.com/symfony/symfony/commit/cf80224589ac05402d4f72f5ddf80900ec94d5ad
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/error-handler/CVE-2020-5274.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2020-5274.yaml
- https://symfony.com/cve-2020-5274

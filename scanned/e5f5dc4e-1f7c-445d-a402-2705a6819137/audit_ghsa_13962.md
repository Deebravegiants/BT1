# [M] Symfony storing cookie headers in HttpCache

## Summary
Severity: Medium
Advisory: GHSA-h7vf-5wrv-9fhv
CVE: CVE-2022-24894
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-h7vf-5wrv-9fhv
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=2.0.0 <4.4.50
- Packagist: `symfony/http-kernel` — affected >=5.0.0 <5.4.20
- Packagist: `symfony/http-kernel` — affected >=6.0.0 <6.0.20
- Packagist: `symfony/http-kernel` — affected >=6.1.0 <6.1.12
- Packagist: `symfony/http-kernel` — affected >=6.2.0 <6.2.6
- Packagist: `symfony/symfony` — affected >=2.0.0 <4.4.50
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.4.20
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.0.20
- Packagist: `symfony/symfony` — affected >=6.1.0 <6.1.12
- Packagist: `symfony/symfony` — affected >=6.2.0 <6.2.6

## Details
Description
-----------

The Symfony HTTP cache system acts as a reverse proxy: it caches HTTP responses (including headers) and returns them to clients.

In a recent `AbstractSessionListener` change, the response might now contain a `Set-Cookie` header. If the Symfony HTTP cache system is enabled, this header might be stored and returned to some other clients. An attacker can use this vulnerability to retrieve the victim's session.

Resolution
----------

The `HttpStore` constructor now takes a parameter containing a list of private headers that are removed from the HTTP response headers.
The default value for this parameter is `Set-Cookie`, but it can be overridden or extended by the application.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/d2f6322af9444ac5cd1ef3ac6f280dbef7f9d1fb) for branch 4.4.

Credits
-------

We would like to thank Soner Sayakci for reporting the issue and Nicolas Grekas for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-h7vf-5wrv-9fhv
- https://nvd.nist.gov/vuln/detail/CVE-2022-24894
- https://github.com/symfony/symfony/commit/d2f6322af9444ac5cd1ef3ac6f280dbef7f9d1fb
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2022-24894.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2022-24894.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2023/07/msg00014.html
- https://symfony.com/cve-2022-24894

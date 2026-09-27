# [H] RCE in Symfony

## Summary
Severity: High
Advisory: GHSA-754h-5r27-7x3r
CVE: CVE-2020-15094
CWE: CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-754h-5r27-7x3r
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=4.3.0 <4.4.13
- Packagist: `symfony/http-kernel` — affected >=5.0.0 <5.1.5
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.4.13
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.1.5

## Details
Description
-----------

The `CachingHttpClient` class from the HttpClient Symfony component relies on the `HttpCache` class to handle requests. `HttpCache` uses internal headers like `X-Body-Eval` and `X-Body-File` to control the restoration of cached responses. The class was initially written with surrogate caching and ESI support in mind (all HTTP calls come from a trusted backend in that scenario). But when used by `CachingHttpClient` and if an attacker can control the response for a request being made by the `CachingHttpClient`, remote code execution is possible.

Resolution
----------

HTTP headers designed for internal use in `HttpCache` are now stripped from remote responses before being passed to `HttpCache`.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/d9910e0b33a2e0f993abff41c6fbc86951b66d78) for the 4.4 branch.

Credits
-------

I would like to thank Matthias Pigulla (webfactory GmbH) for reporting and fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-754h-5r27-7x3r
- https://nvd.nist.gov/vuln/detail/CVE-2020-15094
- https://github.com/symfony/symfony/commit/d9910e0b33a2e0f993abff41c6fbc86951b66d78
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2020-15094.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2020-15094.yaml
- https://github.com/symfony/symfony
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HNGUWOEETOFVH4PN3I3YO4QZHQ4AUKF3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VAQJXAKWPMWB7OL6QPG2ZSEQZYYPU5RC
- https://packagist.org/packages/symfony/http-kernel
- https://packagist.org/packages/symfony/symfony
- https://symfony.com/cve-2020-15094

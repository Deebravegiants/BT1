# [M] Symfony HTTP Foundation web cache poisoning

## Summary
Severity: Medium
Advisory: GHSA-8wgj-6wx8-h5hq
CVE: CVE-2018-14773
CWE: CWE-349
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8wgj-6wx8-h5hq
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.7.0 <2.7.49
- Packagist: `symfony/http-foundation` — affected >=2.8.0 <2.8.44
- Packagist: `symfony/http-foundation` — affected >=3.0.0 <3.3.18
- Packagist: `symfony/http-foundation` — affected >=3.4.0 <3.4.14
- Packagist: `symfony/http-foundation` — affected >=4.0.0 <4.0.14
- Packagist: `symfony/http-foundation` — affected >=4.1.0 <4.1.3
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.49
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.44
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.3.18
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.14
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.14
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.1.3

## Details
An issue was discovered in Http Foundation in Symfony 2.7.0 through 2.7.48, 2.8.0 through 2.8.43, 3.3.0 through 3.3.17, 3.4.0 through 3.4.13, 4.0.0 through 4.0.13, and 4.1.0 through 4.1.2. It arises from support for a (legacy) IIS header that lets users override the path in the request URL via the X-Original-URL or X-Rewrite-URL HTTP request header. These headers are designed for IIS support, but it's not verified that the server is in fact running IIS, which means anybody who can send these requests to an application can trigger this. This affects \Symfony\Component\HttpFoundation\Request::prepareRequestUri() where X-Original-URL and X_REWRITE_URL are both used. The fix drops support for these methods so that they cannot be used as attack vectors such as web cache poisoning.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14773
- https://github.com/symfony/symfony/commit/e447e8b92148ddb3d1956b96638600ec95e08f6b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2018-14773.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-14773.yaml
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://seclists.org/bugtraq/2019/May/21
- https://symfony.com/blog/cve-2018-14773-remove-support-for-legacy-and-risky-http-headers
- https://www.debian.org/security/2019/dsa-4441
- https://www.drupal.org/SA-CORE-2018-005
- http://www.securityfocus.com/bid/104943
- http://www.securitytracker.com/id/1041405

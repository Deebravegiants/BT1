# [M] Webcache Poisoning in symfony/http-kernel

## Summary
Severity: Medium
Advisory: GHSA-q3j3-w37x-hq2q
CVE: CVE-2021-41267
CWE: CWE-444
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-24
Source: https://github.com/advisories/GHSA-q3j3-w37x-hq2q
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=5.2.0 <5.3.12
- Packagist: `symfony/symfony` — affected >=5.2.0 <5.3.12

## Details
Description
-----------

When a Symfony application is running behind a proxy or a load-balancer, you can tell Symfony to look for the `X-Forwarded-*` HTTP headers. HTTP headers that are not part of the "trusted_headers" allowed list are ignored and protect you from "Cache poisoning" attacks. 

In Symfony 5.2, we've added support for the `X-Forwarded-Prefix` header, but this header was accessible in sub-requests, even if it was not part of the "trusted_headers" allowed list. An attacker could leverage this opportunity to forge requests containing a `X-Forwarded-Prefix` HTTP header, leading to a web cache poisoning issue.

Resolution
----------

Symfony now ensures that the `X-Forwarded-Prefix` HTTP header is not forwarded to sub-requests when it is not trusted.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/95dcf51682029e89450aee86267e3d553aa7c487) for branch 5.3.

Credits
-------

We would like to thank Soner Sayakci for reporting the issue and Jérémy Derussé for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-q3j3-w37x-hq2q
- https://nvd.nist.gov/vuln/detail/CVE-2021-41267
- https://github.com/symfony/symfony/pull/44243
- https://github.com/symfony/symfony/commit/95dcf51682029e89450aee86267e3d553aa7c487
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2021-41267.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2021-41267.yaml
- https://github.com/symfony/symfony/releases/tag/v5.3.12
- https://symfony.com/cve-2021-41267

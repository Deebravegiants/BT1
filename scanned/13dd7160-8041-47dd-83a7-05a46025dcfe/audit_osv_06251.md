# [H] cgi.force_redirect configuration is bypassable due to the environment variable collision

## Summary
Severity: High
Advisory: BIT-libphp-2024-8927
Aliases: BIT-php-2024-8927, BIT-php-min-2024-8927, CVE-2024-8927, GHSA-94p6-54jq-9mwp
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-8927
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.12

## Details
In PHP versions 8.1.* before 8.1.30, 8.2.* before 8.2.24, 8.3.* before 8.3.12, HTTP_REDIRECT_STATUS variable is used to check whether or not CGI binary is being run by the HTTP server. However, in certain scenarios, the content of this variable can be controlled by the request submitter via HTTP headers, which can lead to cgi.force_redirect option not being correctly applied. In certain configurations this may lead to arbitrary file inclusion in PHP.

## References
- https://github.com/php/php-src/security/advisories/GHSA-94p6-54jq-9mwp
- https://nvd.nist.gov/vuln/detail/CVE-2024-8927
- https://lists.debian.org/debian-lts-announce/2024/10/msg00011.html
- https://security.netapp.com/advisory/ntap-20241101-0003/

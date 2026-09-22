# [H] Configuring a proxy in a stream context might allow for CRLF injection in URIs

## Summary
Severity: High
Advisory: BIT-libphp-2024-11234
Aliases: BIT-php-2024-11234, BIT-php-min-2024-11234, CVE-2024-11234, GHSA-c5f2-jwm7-mmq2
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-11234
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.14

## Details
In PHP versions 8.1.* before 8.1.31, 8.2.* before 8.2.26, 8.3.* before 8.3.14, when using streams with configured proxy and "request_fulluri" option, the URI is not properly sanitized which can lead to HTTP request smuggling and allow the attacker to use the proxy to perform arbitrary HTTP requests originating from the server, thus potentially gaining access to resources not normally available to the external user.

## References
- https://github.com/php/php-src/security/advisories/GHSA-c5f2-jwm7-mmq2
- https://nvd.nist.gov/vuln/detail/CVE-2024-11234
- https://lists.debian.org/debian-lts-announce/2024/12/msg00007.html
- https://security.netapp.com/advisory/ntap-20241220-0008/

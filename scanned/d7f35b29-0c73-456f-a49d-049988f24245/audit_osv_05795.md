# [H] BIT-haproxy-2023-0836

## Summary
Severity: High
Advisory: BIT-haproxy-2023-0836
Aliases: CVE-2023-0836
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-0836
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.7.0 <2.7.1

## Details
An information leak vulnerability was discovered in HAProxy 2.1, 2.2 before 2.2.27, 2.3, 2.4 before 2.4.21, 2.5 before 2.5.11, 2.6 before 2.6.8, 2.7 before 2.7.1. There are 5 bytes left uninitialized in the connection buffer when encoding the FCGI_BEGIN_REQUEST record. Sensitive data may be disclosed to configured FastCGI backends in an unexpected way.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commitdiff%3Bh=2e6bf0a
- https://www.debian.org/security/2023/dsa-5388
- https://nvd.nist.gov/vuln/detail/CVE-2023-0836

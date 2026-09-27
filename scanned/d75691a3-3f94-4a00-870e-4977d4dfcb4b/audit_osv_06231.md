# [M] Potential buffer overflow in php_cli_server_startup_workers

## Summary
Severity: Medium
Advisory: BIT-libphp-2022-4900
Aliases: BIT-php-2022-4900, BIT-php-min-2022-4900, CVE-2022-4900
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-4900
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <8.0.22

## Details
A vulnerability was found in PHP where setting the environment variable PHP_CLI_SERVER_WORKERS to a large value leads to a heap buffer overflow.

## References
- https://access.redhat.com/security/cve/CVE-2022-4900
- https://bugzilla.redhat.com/show_bug.cgi?id=2179880
- https://nvd.nist.gov/vuln/detail/CVE-2022-4900
- https://security.netapp.com/advisory/ntap-20231130-0008/
- https://lists.debian.org/debian-lts-announce/2024/10/msg00011.html
- https://github.com/php/php-src/commit/789a37f14405e2d1a05a76c9fb4ed2d49d4580d5
- https://github.com/php/php-src/commit/82effb3fc7bcab0efcc343b3e03355f5f2f663c9

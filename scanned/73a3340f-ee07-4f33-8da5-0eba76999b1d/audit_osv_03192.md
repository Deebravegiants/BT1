# [M] ALPINE-CVE-2025-14017

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14017
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14017
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.17.0 <8.18.0-r0
- Alpine:v3.24: `curl` — affected >=7.17.0 <8.18.0-r0

## Details
When doing multi-threaded LDAPS transfers (LDAP over TLS) with libcurl,
changing TLS options in one thread would inadvertently change them globally
and therefore possibly also affect other concurrently setup transfers.

Disabling certificate verification for a specific transfer could
unintentionally disable the feature for other threads as well.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14017

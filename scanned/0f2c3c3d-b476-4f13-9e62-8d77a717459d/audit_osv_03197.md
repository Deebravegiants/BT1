# [M] ALPINE-CVE-2025-14831

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14831
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14831
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.12-r0

## Details
A flaw was found in GnuTLS. This vulnerability allows a denial of service (DoS) by excessive CPU (Central Processing Unit) and memory consumption via specially crafted malicious certificates containing a large number of name constraints and subject alternative names (SANs).

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14831

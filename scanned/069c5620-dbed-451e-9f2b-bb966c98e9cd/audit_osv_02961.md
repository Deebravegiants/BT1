# [H] ALPINE-CVE-2024-0567

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-0567
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0567
Type: osv

## Affected
- Alpine:v3.18: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.19: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.20: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.21: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.22: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.23: `gnutls` — affected >=3.7.0 <3.8.3-r0
- Alpine:v3.24: `gnutls` — affected >=3.7.0 <3.8.3-r0

## Details
A vulnerability was found in GnuTLS, where a cockpit (which uses gnuTLS) rejects a certificate chain with distributed trust. This issue occurs when validating a certificate chain with cockpit-certificate-ensure. This flaw allows an unauthenticated, remote client or attacker to initiate a denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0567

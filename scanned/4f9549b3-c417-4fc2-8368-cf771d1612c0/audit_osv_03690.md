# [H] ALPINE-CVE-2026-42012

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42012
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42012
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.13-r0

## Details
A flaw was found in gnutls. A remote attacker could exploit this vulnerability by presenting a specially crafted certificate that contains Uniform Resource Identifier (URI) or Service (SRV) Subject Alternative Names (SANs). This could cause the certificate validation process to incorrectly fall back to checking DNS hostnames against the Common Name (CN), potentially allowing the attacker to spoof legitimate services or intercept sensitive information.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42012

# [H] ALPINE-CVE-2026-3833

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3833
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3833
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.13-r0

## Details
A flaw was found in gnutls. This vulnerability occurs because gnutls performs case-sensitive comparisons of `nameConstraints` labels, specifically for `dNSName` (DNS) or `rfc822Name` (email) constraints within `excludedSubtrees` or `permittedSubtrees`. A remote attacker can exploit this by crafting a leaf certificate with casing differences in the Subject Alternative Name (SAN), leading to a policy bypass where a certificate that should be rejected is instead accepted. This could result in unauthorized access or information disclosure.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3833

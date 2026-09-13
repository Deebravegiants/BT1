# [H] ALPINE-CVE-2022-41916

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41916
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41916
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0

## Details
Heimdal is an implementation of ASN.1/DER, PKIX, and Kerberos. Versions prior to 7.7.1 are vulnerable to a denial of service vulnerability in Heimdal's PKI certificate validation library, affecting the KDC (via PKINIT) and kinit (via PKINIT), as well as any third-party applications using Heimdal's libhx509. Users should upgrade to Heimdal 7.7.1 or 7.8. There are no known workarounds for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41916

# [M] ALPINE-CVE-2024-12133

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-12133
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12133
Type: osv

## Affected
- Alpine:v3.18: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.19: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.20: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.21: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.22: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.23: `libtasn1` — affected >=0 <4.20.0-r0
- Alpine:v3.24: `libtasn1` — affected >=0 <4.20.0-r0

## Details
A flaw in libtasn1 causes inefficient handling of specific certificate data. When processing a large number of elements in a certificate, libtasn1 takes much longer than expected, which can slow down or even crash the system. This flaw allows an attacker to send a specially crafted certificate, causing a denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12133

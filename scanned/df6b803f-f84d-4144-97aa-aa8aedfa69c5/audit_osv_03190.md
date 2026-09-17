# [H] ALPINE-CVE-2025-13151

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-13151
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-13151
Type: osv

## Affected
- Alpine:v3.20: `libtasn1` — affected >=0 <4.21.0-r0
- Alpine:v3.21: `libtasn1` — affected >=0 <4.21.0-r0
- Alpine:v3.22: `libtasn1` — affected >=0 <4.21.0-r0
- Alpine:v3.23: `libtasn1` — affected >=0 <4.21.0-r0
- Alpine:v3.24: `libtasn1` — affected >=0 <4.21.0-r0

## Details
Stack-based buffer overflow in libtasn1 version: v4.20.0. The function fails to validate the size of input data resulting in a buffer overflow in asn1_expend_octet_string.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-13151

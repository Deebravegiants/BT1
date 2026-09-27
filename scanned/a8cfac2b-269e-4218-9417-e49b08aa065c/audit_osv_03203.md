# [M] ALPINE-CVE-2025-1632

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-1632
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-1632
Type: osv

## Affected
- Alpine:v3.18: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.19: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.20: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.21: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.22: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.23: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.24: `libarchive` — affected >=0 <3.7.9-r0

## Details
A vulnerability was found in libarchive up to 3.7.7. It has been classified as problematic. This affects the function list of the file bsdunzip.c. The manipulation leads to null pointer dereference. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-1632

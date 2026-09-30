# [H] ALPINE-CVE-2019-3863

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-3863
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3863
Type: osv

## Affected
- Alpine:v3.10: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.11: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.12: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.13: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.14: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.15: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.16: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.17: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.18: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.19: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.20: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.21: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.22: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.23: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.24: `libssh2` — affected >=0 <1.8.1-r0
- Alpine:v3.9: `libssh2` — affected >=0 <1.8.1-r0

## Details
A flaw was found in libssh2 before 1.8.1 creating a vulnerability on the SSH client side. A server could send a multiple keyboard interactive response messages whose total length are greater than unsigned char max characters. This value is used by the SSH client as an index to copy memory causing in an out of bounds memory write error.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3863

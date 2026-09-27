# [C] ALPINE-CVE-2021-3520

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-3520
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3520
Type: osv

## Affected
- Alpine:v3.12: `lz4` — affected >=1.8.3 <1.9.2-r1
- Alpine:v3.13: `lz4` — affected >=1.8.3 <1.9.2-r1
- Alpine:v3.14: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.15: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.16: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.17: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.18: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.19: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.20: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.21: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.22: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.23: `lz4` — affected >=1.8.3 <1.9.3-r1
- Alpine:v3.24: `lz4` — affected >=1.8.3 <1.9.3-r1

## Details
There's a flaw in lz4. An attacker who submits a crafted file to an application linked with lz4 may be able to trigger an integer overflow, leading to calling of memmove() on a negative size argument, causing an out-of-bounds write and/or a crash. The greatest impact of this flaw is to availability, with some potential impact to confidentiality and integrity as well.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3520

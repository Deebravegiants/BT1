# [H] ALPINE-CVE-2019-17543

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17543
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17543
Type: osv

## Affected
- Alpine:v3.10: `lz4` — affected >=0 <1.9.1-r1
- Alpine:v3.11: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.12: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.13: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.14: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.15: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.16: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.17: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.18: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.19: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.20: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.21: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.22: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.23: `lz4` — affected >=0 <1.9.2-r0
- Alpine:v3.24: `lz4` — affected >=0 <1.9.2-r0

## Details
LZ4 before 1.9.2 has a heap-based buffer overflow in LZ4_write32 (related to LZ4_compress_destSize), affecting applications that call LZ4_compress_fast with a large input. (This issue can also lead to data corruption.) NOTE: the vendor states "only a few specific / uncommon usages of the API are at risk."

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17543

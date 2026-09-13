# [M] ALPINE-CVE-2026-34743

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34743
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34743
Type: osv

## Affected
- Alpine:v3.20: `xz` — affected >=0 <5.8.3-r0
- Alpine:v3.21: `xz` — affected >=0 <5.8.3-r0
- Alpine:v3.22: `xz` — affected >=0 <5.8.3-r0
- Alpine:v3.23: `xz` — affected >=0 <5.8.3-r0
- Alpine:v3.24: `xz` — affected >=0 <5.8.3-r0

## Details
XZ Utils provide a general-purpose data-compression library plus command-line tools. Prior to version 5.8.3, if lzma_index_decoder() was used to decode an Index that contained no Records, the resulting lzma_index was left in a state where where a subsequent lzma_index_append() would allocate too little memory, and a buffer overflow would occur. This issue has been patched in version 5.8.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34743

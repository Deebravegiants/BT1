# [M] ALPINE-CVE-2024-41957

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-41957
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-41957
Type: osv

## Affected
- Alpine:v3.20: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.21: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.0652-r0

## Details
Vim is an open source command line text editor. Vim < v9.1.0647 has double free in src/alloc.c:616. When closing a window, the corresponding tagstack data will be cleared and freed. However a bit later, the quickfix list belonging to that window will also be cleared and if that quickfix list points to the same tagstack data, Vim will try to free it again, resulting in a double-free/use-after-free access exception. Impact is low since the user must intentionally execute vim with several non-default flags,
but it may cause a crash of Vim. The issue has been fixed as of Vim patch v9.1.0647

## References
- https://security.alpinelinux.org/vuln/CVE-2024-41957

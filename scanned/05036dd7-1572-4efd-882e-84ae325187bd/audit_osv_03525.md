# [M] ALPINE-CVE-2026-25749

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-25749
Ecosystem: Alpine:v3.23
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-25749
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.1.2132-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.1.2132, a heap buffer overflow vulnerability exists in Vim's tag file resolution logic when processing the 'helpfile' option. The vulnerability is located in the get_tagfname() function in src/tag.c. When processing help file tags, Vim copies the user-controlled 'helpfile' option value into a fixed-size heap buffer of MAXPATHL + 1 bytes (typically 4097 bytes) using an unsafe STRCPY() operation without any bounds checking. This issue has been patched in version 9.1.2132.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-25749

# [M] ALPINE-CVE-2026-57452

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-57452
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57452
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0671, when Vim opens a file encrypted with the VimCrypt~04! or VimCrypt~05!
method (xchacha20poly1305, requires the +sodium feature) whose body is shorter than a single libsodium secretstream header, an unsigned length calculation underflows and a subsequent decryption call reads far past the end of the input buffer, crashing Vim. This vulnerability is fixed in 9.2.0671.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57452

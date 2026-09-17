# [M] ALPINE-CVE-2026-57451

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-57451
Ecosystem: Alpine:v3.23
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57451
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0670, get_text_props() in src/textprop.c reads a uint16 property count stored inline after a line's text and returns it as the number of 32-byte textprop_T entries that follow. The only check is a floor that guarantees room for a single entry; the count is never checked against the amount of data actually present. A line that declares a large count while carrying little data causes consumers to read far past the end of the line buffer. Such a line can be delivered through a crafted undo file, leading to a crash. This vulnerability is fixed in 9.2.0670.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57451

# [H] ALPINE-CVE-2026-55895

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-55895
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-55895
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0663, a Vimscript code injection vulnerability exists in s:NetrwLocalRmFile() in the netrw plugin (runtime/pack/dist/opt/netrw/autoload/netrw.vim) when deleting a local file from the browser. A filename derived from the buffer's directory listing is interpolated into an Ex command line passed to :execute with only the backslash character escaped, allowing a crafted filename containing a bar (|) to terminate the intended command and execute arbitrary Vimscript, including shell commands via :call system() and :!.  This vulnerability is fixed in 9.2.0663.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-55895

# [H] ALPINE-CVE-2026-46483

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-46483
Ecosystem: Alpine:v3.23
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-46483
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0481-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0479, a command injection vulnerability exists in tar#Vimuntar() in
runtime/autoload/tar.vim when decompressing .tgz archives on Unix-like systems. The function builds :!gunzip and :!gzip -d commands using shellescape(tartail) without the {special} flag, allowing a crafted archive filename to trigger Vim cmdline-special expansion and execute shell commands in the user's context. This vulnerability is fixed in 9.2.0479.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-46483

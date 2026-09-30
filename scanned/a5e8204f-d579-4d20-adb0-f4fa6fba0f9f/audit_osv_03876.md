# [H] ALPINE-CVE-2026-59858

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-59858
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59858
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0735, the C omni-completion script in runtime/autoload/ccomplete.vim interpolates the typeref: or typename: extension field of a tags entry, without escaping, into a :vimgrep pattern that is run through :execute. Because :vimgrep honors the bar as a command separator, a crafted tag field can close the search pattern and append an arbitrary Ex command; opening a hostile .c file whose project tags file contains such an entry and invoking C omni-completion runs that command as the editing user. This issue is fixed in version 9.2.0735.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59858

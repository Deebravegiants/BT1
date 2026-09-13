# [H] ALPINE-CVE-2026-39881

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-39881
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39881
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0321-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0316, a command injection vulnerability in Vim's netbeans interface allows a malicious netbeans server to execute arbitrary Ex commands when Vim connects to it, via unsanitized strings in the defineAnnoType and specialKeys protocol messages. This vulnerability is fixed in 9.2.0316.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39881

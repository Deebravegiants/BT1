# [C] ALPINE-CVE-2026-28780

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-28780
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28780
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.67-r0

## Details
Heap-based Buffer Overflow vulnerability in mod_proxy_ajp of Apache HTTP Server.
If mod_proxy_ajp connects to a malicious AJP server this AJP server can send a malicious AJP message back to mod_proxy_ajp and cause it to write 4 attacker controlled bytes after the end of a heap based buffer.

This issue affects Apache HTTP Server: through 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28780

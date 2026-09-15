# [H] CVE-2019-6706

## Summary
Severity: High
Advisory: CVE-2019-6706
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-23
Source: https://osv.dev/vulnerability/CVE-2019-6706
Type: osv

## Details
Lua 5.3.5 has a use-after-free in lua_upvaluejoin in lapi.c. For example, a crash outcome might be achieved by an attacker who is able to trigger a debug.upvaluejoin call in which the arguments have certain relationships.

## References
- http://lua-users.org/lists/lua-l/2019-01/msg00039.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00031.html
- https://access.redhat.com/security/cve/cve-2019-6706
- https://github.com/lua/lua/commit/89aee84cbc9224f638f3b7951b306d2ee8ecb71e
- http://packetstormsecurity.com/files/151335/Lua-5.3.5-Use-After-Free.html
- https://github.com/Lua-Project/cve-analysis/blob/a43c9ccd00274b31fa2f24c6c8f20ce36655682d/CVE-2019-6706.pdf

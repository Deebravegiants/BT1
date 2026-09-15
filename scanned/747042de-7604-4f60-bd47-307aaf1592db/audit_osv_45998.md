# [M] JLSEC-2026-556

## Summary
Severity: Medium
Advisory: JLSEC-2026-556
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-556
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=5.4.3+0 <5.4.4+0

## Details
Stack overflow in `lua_resume` of ldo.c in Lua Interpreter 5.1.0~5.4.4 allows attackers to perform a Denial of Service via a crafted script file.

## References
- http://lua-users.org/lists/lua-l/2021-10/msg00123.html
- http://lua-users.org/lists/lua-l/2021-11/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7XHFYHGSZKL53VCLSJSAJ6VMFGAIXKO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3EMGAQ5Y6GXJLY4K5DUOOEQT4MZ4J4F/

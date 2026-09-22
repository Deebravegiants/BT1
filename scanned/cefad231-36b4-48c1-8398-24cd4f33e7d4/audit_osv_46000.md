# [M] JLSEC-2026-558

## Summary
Severity: Medium
Advisory: JLSEC-2026-558
Ecosystem: Julia
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-558
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=5.4.3+0 <5.4.4+0

## Details
Use after free in garbage collector and finalizer of lgc.c in Lua interpreter 5.4.0~5.4.3 allows attackers to perform Sandbox Escape via a crafted script file.

## References
- http://lua-users.org/lists/lua-l/2021-11/msg00186.html
- http://lua-users.org/lists/lua-l/2021-12/msg00007.html
- http://lua-users.org/lists/lua-l/2021-12/msg00015.html
- http://lua-users.org/lists/lua-l/2021-12/msg00030.html
- https://github.com/Lua-Project/lua-5.4.4-sandbox-escape-with-new-vulnerability

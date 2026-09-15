# [M] JLSEC-2026-554

## Summary
Severity: Medium
Advisory: JLSEC-2026-554
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-554
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=0 <5.4.3+0

## Details
Lua 5.4.0 (fixed in 5.4.1) has a segmentation fault in changedline in ldebug.c (e.g., when called by `luaG_traceexec`) because it incorrectly expects that an oldpc value is always updated upon a return of the flow of control to a function.

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00123.html
- https://github.com/lua/lua/commit/a2195644d89812e5b157ce7bac35543e06db05e3
- https://www.lua.org/bugs.html#5.4.0-8

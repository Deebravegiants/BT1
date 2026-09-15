# [M] BIT-lua-2020-15945

## Summary
Severity: Medium
Advisory: BIT-lua-2020-15945
Aliases: CVE-2020-15945
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-15945
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.3.1 <5.4.0

## Details
Lua 5.4.0 (fixed in 5.4.1) has a segmentation fault in changedline in ldebug.c (e.g., when called by luaG_traceexec) because it incorrectly expects that an oldpc value is always updated upon a return of the flow of control to a function.

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00123.html
- https://github.com/lua/lua/commit/a2195644d89812e5b157ce7bac35543e06db05e3
- https://www.lua.org/bugs.html#5.4.0-8
- https://nvd.nist.gov/vuln/detail/CVE-2020-15945

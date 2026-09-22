# [M] BIT-lua-2020-24371

## Summary
Severity: Medium
Advisory: BIT-lua-2020-24371
Aliases: CVE-2020-24371
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-24371
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
lgc.c in Lua 5.4.0 mishandles the interaction between barriers and the sweep phase, leading to a memory access violation involving collectgarbage.

## References
- https://github.com/lua/lua/commit/a6da1472c0c5e05ff249325f979531ad51533110
- https://www.lua.org/bugs.html#5.4.0-10
- https://nvd.nist.gov/vuln/detail/CVE-2020-24371

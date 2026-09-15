# [H] BIT-lua-2020-24342

## Summary
Severity: High
Advisory: BIT-lua-2020-24342
Aliases: CVE-2020-24342
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-24342
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
Lua through 5.4.0 allows a stack redzone cross in luaO_pushvfstring because a protection mechanism wrongly calls luaD_callnoyield twice in a row.

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00052.html
- https://github.com/lua/lua/commit/34affe7a63fc5d842580a9f23616d057e17dfe27
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QA5Q5MDQMTGXRQO3PAQ4EZFTYWJXZM5N/
- https://nvd.nist.gov/vuln/detail/CVE-2020-24342

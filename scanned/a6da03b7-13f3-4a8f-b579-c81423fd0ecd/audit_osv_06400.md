# [H] BIT-lua-2020-15888

## Summary
Severity: High
Advisory: BIT-lua-2020-15888
Aliases: CVE-2020-15888
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-15888
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
Lua through 5.4.0 mishandles the interaction between stack resizes and garbage collection, leading to a heap-based buffer overflow, heap-based buffer over-read, or use-after-free.

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00053.html
- http://lua-users.org/lists/lua-l/2020-07/msg00054.html
- http://lua-users.org/lists/lua-l/2020-07/msg00071.html
- http://lua-users.org/lists/lua-l/2020-07/msg00079.html
- https://github.com/lua/lua/commit/6298903e35217ab69c279056f925fb72900ce0b7
- https://github.com/lua/lua/commit/eb41999461b6f428186c55abd95f4ce1a76217d5
- https://nvd.nist.gov/vuln/detail/CVE-2020-15888

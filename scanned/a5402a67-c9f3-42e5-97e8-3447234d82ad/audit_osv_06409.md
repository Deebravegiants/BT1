# [M] BIT-lua-2021-44964

## Summary
Severity: Medium
Advisory: BIT-lua-2021-44964
Aliases: CVE-2021-44964
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2021-44964
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.4

## Details
Use after free in garbage collector and finalizer of lgc.c in Lua interpreter 5.4.0~5.4.3 allows attackers to perform Sandbox Escape via a crafted script file.

## References
- http://lua-users.org/lists/lua-l/2021-11/msg00186.html
- http://lua-users.org/lists/lua-l/2021-12/msg00007.html
- http://lua-users.org/lists/lua-l/2021-12/msg00015.html
- http://lua-users.org/lists/lua-l/2021-12/msg00030.html
- https://github.com/Lua-Project/lua-5.4.4-sandbox-escape-with-new-vulnerability
- https://nvd.nist.gov/vuln/detail/CVE-2021-44964

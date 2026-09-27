# [H] BIT-lua-2022-33099

## Summary
Severity: High
Advisory: BIT-lua-2022-33099
Aliases: CVE-2022-33099
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2022-33099
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.2 <5.4.5

## Details
An issue in the component luaG_runerror of Lua v5.4.4 and below leads to a heap-buffer overflow when a recursive error occurs.

## References
- https://github.com/lua/lua/commit/42d40581dd919fb134c07027ca1ce0844c670daf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJNJ66IFDUKWJJZXHGOLRGIA3HWWC36R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHYZOEFDVLVAD6EEP4CDW6DNONIVVHPA/
- https://lua-users.org/lists/lua-l/2022-05/msg00035.html
- https://lua-users.org/lists/lua-l/2022-05/msg00042.html
- https://lua-users.org/lists/lua-l/2022-05/msg00073.html
- https://www.lua.org/bugs.html#Lua-stack%20overflow%20when%20C%20stack%20overflows%20while%20handling%20an%20error:~:text=Lua-stack%20overflow%20when%20C%20stack%20overflows%20while%20handling%20an%20error
- https://nvd.nist.gov/vuln/detail/CVE-2022-33099

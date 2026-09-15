# [H] JLSEC-2026-561

## Summary
Severity: High
Advisory: JLSEC-2026-561
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-561
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=5.4.3+0 <5.4.6+0

## Details
An issue in the component `luaG_runerror` of Lua v5.4.4 and below leads to a heap-buffer overflow when a recursive error occurs.

## References
- https://github.com/lua/lua/commit/42d40581dd919fb134c07027ca1ce0844c670daf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJNJ66IFDUKWJJZXHGOLRGIA3HWWC36R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHYZOEFDVLVAD6EEP4CDW6DNONIVVHPA/
- https://lua-users.org/lists/lua-l/2022-05/msg00035.html
- https://lua-users.org/lists/lua-l/2022-05/msg00042.html
- https://lua-users.org/lists/lua-l/2022-05/msg00073.html
- https://www.lua.org/bugs.html#Lua-stack%20overflow%20when%20C%20stack%20overflows%20while%20handling%20an%20error:~:text=Lua-stack%20overflow%20when%20C%20stack%20overflows%20while%20handling%20an%20error

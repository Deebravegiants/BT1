# [C] JLSEC-2026-560

## Summary
Severity: Critical
Advisory: JLSEC-2026-560
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-560
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=5.4.3+0 <5.4.6+0

## Details
singlevar in lparser.c in Lua from (including) 5.4.0 up to (excluding) 5.4.4 lacks a certain `luaK_exp2anyregup` call, leading to a heap-based buffer over-read that might affect a system that compiles untrusted Lua code.

## References
- https://github.com/lua/lua/commit/1f3c6f4534c6411313361697d98d1145a1f030fa
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJNJ66IFDUKWJJZXHGOLRGIA3HWWC36R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHYZOEFDVLVAD6EEP4CDW6DNONIVVHPA/
- https://lua-users.org/lists/lua-l/2022-02/msg00001.html
- https://lua-users.org/lists/lua-l/2022-02/msg00070.html
- https://lua-users.org/lists/lua-l/2022-04/msg00009.html
- https://security.gentoo.org/glsa/202305-23

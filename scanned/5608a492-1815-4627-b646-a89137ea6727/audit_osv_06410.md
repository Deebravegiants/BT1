# [C] BIT-lua-2022-28805

## Summary
Severity: Critical
Advisory: BIT-lua-2022-28805
Aliases: CVE-2022-28805
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2022-28805
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.5

## Details
singlevar in lparser.c in Lua from (including) 5.4.0 up to (excluding) 5.4.4 lacks a certain luaK_exp2anyregup call, leading to a heap-based buffer over-read that might affect a system that compiles untrusted Lua code.

## References
- https://github.com/lua/lua/commit/1f3c6f4534c6411313361697d98d1145a1f030fa
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJNJ66IFDUKWJJZXHGOLRGIA3HWWC36R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHYZOEFDVLVAD6EEP4CDW6DNONIVVHPA/
- https://lua-users.org/lists/lua-l/2022-02/msg00001.html
- https://lua-users.org/lists/lua-l/2022-02/msg00070.html
- https://lua-users.org/lists/lua-l/2022-04/msg00009.html
- https://security.gentoo.org/glsa/202305-23
- https://nvd.nist.gov/vuln/detail/CVE-2022-28805

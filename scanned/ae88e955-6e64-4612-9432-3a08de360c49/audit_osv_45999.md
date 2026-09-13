# [M] JLSEC-2026-557

## Summary
Severity: Medium
Advisory: JLSEC-2026-557
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-557
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=5.4.3+0 <5.4.4+0

## Details
Lua v5.4.3 and above are affected by SEGV by type confusion in funcnamefromcode function in ldebug.c which can cause a local denial of service.

## References
- http://lua-users.org/lists/lua-l/2021-11/msg00195.html
- http://lua-users.org/lists/lua-l/2021-11/msg00204.html
- https://access.redhat.com/security/cve/cve-2021-44647
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3EMGAQ5Y6GXJLY4K5DUOOEQT4MZ4J4F/
- https://security.gentoo.org/glsa/202305-23

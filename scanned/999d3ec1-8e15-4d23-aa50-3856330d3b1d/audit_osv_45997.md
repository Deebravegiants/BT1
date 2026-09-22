# [M] JLSEC-2026-555

## Summary
Severity: Medium
Advisory: JLSEC-2026-555
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-555
Type: osv

## Affected
- Julia: `Lua_jll` — affected >=0 <5.3.6+0

## Details
ldebug.c in Lua 5.4.0 allows a negation overflow and segmentation fault in getlocal and setlocal, as demonstrated by getlocal(3,2^31).

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00324.html
- https://github.com/lua/lua/commit/a585eae6e7ada1ca9271607a4f48dfb17868ab7b
- https://lists.debian.org/debian-lts-announce/2020/09/msg00019.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E6KONNG6UEI3FMEOY67NDZC32NBGBI44/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QXYMCIUNGK26VHAYHGP5LPW56G2KWOHQ/

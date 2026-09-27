# [M] BIT-lua-2020-24370

## Summary
Severity: Medium
Advisory: BIT-lua-2020-24370
Aliases: CVE-2020-24370
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-24370
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
ldebug.c in Lua 5.4.0 allows a negation overflow and segmentation fault in getlocal and setlocal, as demonstrated by getlocal(3,2^31).

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00324.html
- https://github.com/lua/lua/commit/a585eae6e7ada1ca9271607a4f48dfb17868ab7b
- https://lists.debian.org/debian-lts-announce/2020/09/msg00019.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E6KONNG6UEI3FMEOY67NDZC32NBGBI44/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QXYMCIUNGK26VHAYHGP5LPW56G2KWOHQ/
- https://nvd.nist.gov/vuln/detail/CVE-2020-24370

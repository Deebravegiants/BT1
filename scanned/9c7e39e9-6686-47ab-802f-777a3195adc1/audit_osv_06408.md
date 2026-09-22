# [M] BIT-lua-2021-44647

## Summary
Severity: Medium
Advisory: BIT-lua-2021-44647
Aliases: CVE-2021-44647
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2021-44647
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.3 <5.4.4

## Details
Lua v5.4.3 and above are affected by SEGV by type confusion in funcnamefromcode function in ldebug.c which can cause a local denial of service.

## References
- http://lua-users.org/lists/lua-l/2021-11/msg00195.html
- http://lua-users.org/lists/lua-l/2021-11/msg00204.html
- https://access.redhat.com/security/cve/cve-2021-44647
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3EMGAQ5Y6GXJLY4K5DUOOEQT4MZ4J4F/
- https://security.gentoo.org/glsa/202305-23
- https://nvd.nist.gov/vuln/detail/CVE-2021-44647

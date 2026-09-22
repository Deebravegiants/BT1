# [M] BIT-lua-2021-43519

## Summary
Severity: Medium
Advisory: BIT-lua-2021-43519
Aliases: CVE-2021-43519
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2021-43519
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.4

## Details
Stack overflow in lua_resume of ldo.c in Lua Interpreter 5.1.0~5.4.4 allows attackers to perform a Denial of Service via a crafted script file.

## References
- http://lua-users.org/lists/lua-l/2021-10/msg00123.html
- http://lua-users.org/lists/lua-l/2021-11/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7XHFYHGSZKL53VCLSJSAJ6VMFGAIXKO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3EMGAQ5Y6GXJLY4K5DUOOEQT4MZ4J4F/
- https://nvd.nist.gov/vuln/detail/CVE-2021-43519

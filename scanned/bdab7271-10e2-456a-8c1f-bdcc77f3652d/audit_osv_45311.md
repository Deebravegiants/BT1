# [H] libexpat through 2.6.1 allows an XML Entity Expansion attack when there is isolated use of external...

## Summary
Severity: High
Advisory: JLSEC-2025-61
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-61
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.6.2+0

## Details
libexpat through 2.6.1 allows an XML Entity Expansion attack when there is isolated use of external parsers (created via `XML_ExternalEntityParserCreate`).

## References
- http://www.openwall.com/lists/oss-security/2024/03/15/1
- https://github.com/libexpat/libexpat/issues/839
- https://github.com/libexpat/libexpat/pull/842
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPLC6WDSRDUYS7F7JWAOVOHFNOUQ43DD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LKJ7V5F6LJCEQJXDBWGT27J7NAP3E3N7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VK2O34GH43NTHBZBN7G5Y6YKJKPUCTBE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FPLC6WDSRDUYS7F7JWAOVOHFNOUQ43DD/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LKJ7V5F6LJCEQJXDBWGT27J7NAP3E3N7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VK2O34GH43NTHBZBN7G5Y6YKJKPUCTBE/
- https://security.netapp.com/advisory/ntap-20240322-0001/

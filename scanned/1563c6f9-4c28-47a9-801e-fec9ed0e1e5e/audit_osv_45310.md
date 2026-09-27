# [H] libexpat through 2.5.0 allows a denial of service (resource consumption) because many full...

## Summary
Severity: High
Advisory: JLSEC-2025-60
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-60
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.6.2+0

## Details
libexpat through 2.5.0 allows a denial of service (resource consumption) because many full reparsings are required in the case of a large token for which multiple buffer fills are needed.

## References
- http://www.openwall.com/lists/oss-security/2024/03/20/5
- https://github.com/libexpat/libexpat/pull/789
- https://lists.debian.org/debian-lts-announce/2024/04/msg00006.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PNRIHC7DVVRAIWFRGV23Y6UZXFBXSQDB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WNUBSGZFEZOBHJFTAD42SAN4ATW2VEMV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PNRIHC7DVVRAIWFRGV23Y6UZXFBXSQDB/
- https://security.netapp.com/advisory/ntap-20240614-0003/

# [H] JLSEC-2026-165

## Summary
Severity: High
Advisory: JLSEC-2026-165
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/JLSEC-2026-165
Type: osv

## Affected
- Julia: `OpenLDAPClient_jll` — affected >=0 <2.5.14+0

## Details
A flaw was discovered in OpenLDAP before 2.4.57 leading to a slapd crash in the Values Return Filter control handling, resulting in denial of service (double free and out-of-bounds read).

## References
- http://seclists.org/fulldisclosure/2021/May/64
- http://seclists.org/fulldisclosure/2021/May/65
- http://seclists.org/fulldisclosure/2021/May/70
- https://bugs.openldap.org/show_bug.cgi?id=9408
- https://git.openldap.org/openldap/openldap/-/commit/21981053a1195ae1555e23df4d9ac68d34ede9dd
- https://git.openldap.org/openldap/openldap/-/tags/OPENLDAP_REL_ENG_2_4_57
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/02/msg00005.html
- https://security.netapp.com/advisory/ntap-20210226-0002/
- https://support.apple.com/kb/HT212529
- https://support.apple.com/kb/HT212530
- https://support.apple.com/kb/HT212531
- https://www.debian.org/security/2021/dsa-4845

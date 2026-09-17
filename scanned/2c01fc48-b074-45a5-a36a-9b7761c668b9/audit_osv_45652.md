# [H] JLSEC-2026-166

## Summary
Severity: High
Advisory: JLSEC-2026-166
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/JLSEC-2026-166
Type: osv

## Affected
- Julia: `OpenLDAPClient_jll` — affected >=0 <2.5.14+0

## Details
A flaw was discovered in OpenLDAP before 2.4.57 leading to an invalid pointer free and slapd crash in the saslAuthzTo processing, resulting in denial of service.

## References
- http://seclists.org/fulldisclosure/2021/May/64
- http://seclists.org/fulldisclosure/2021/May/65
- http://seclists.org/fulldisclosure/2021/May/70
- https://bugs.openldap.org/show_bug.cgi?id=9409
- https://git.openldap.org/openldap/openldap/-/commit/554dff1927176579d652f2fe60c90e9abbad4c65
- https://git.openldap.org/openldap/openldap/-/commit/5a2017d4e61a6ddc4dcb4415028e0d08eb6bca26
- https://git.openldap.org/openldap/openldap/-/commit/c0b61a9486508e5202aa2e0cfb68c9813731b439
- https://git.openldap.org/openldap/openldap/-/commit/d169e7958a3e0dc70f59c8374bf8a59833b7bdd8
- https://git.openldap.org/openldap/openldap/-/tags/OPENLDAP_REL_ENG_2_4_57
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/02/msg00005.html
- https://security.netapp.com/advisory/ntap-20210226-0002/
- https://support.apple.com/kb/HT212529
- https://support.apple.com/kb/HT212530
- https://support.apple.com/kb/HT212531
- https://www.debian.org/security/2021/dsa-4845

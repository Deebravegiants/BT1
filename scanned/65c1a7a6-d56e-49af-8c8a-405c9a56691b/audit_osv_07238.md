# [H] BIT-openldap-2020-36227

## Summary
Severity: High
Advisory: BIT-openldap-2020-36227
Aliases: CVE-2020-36227
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-36227
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.57

## Details
A flaw was discovered in OpenLDAP before 2.4.57 leading to an infinite loop in slapd with the cancel_extop Cancel operation, resulting in denial of service.

## References
- http://seclists.org/fulldisclosure/2021/May/64
- http://seclists.org/fulldisclosure/2021/May/65
- http://seclists.org/fulldisclosure/2021/May/70
- https://bugs.openldap.org/show_bug.cgi?id=9428
- https://git.openldap.org/openldap/openldap/-/commit/9d0e8485f3113505743baabf1167e01e4558ccf5
- https://git.openldap.org/openldap/openldap/-/tags/OPENLDAP_REL_ENG_2_4_57
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/02/msg00005.html
- https://security.netapp.com/advisory/ntap-20210226-0002/
- https://support.apple.com/kb/HT212529
- https://support.apple.com/kb/HT212530
- https://support.apple.com/kb/HT212531
- https://www.debian.org/security/2021/dsa-4845
- https://nvd.nist.gov/vuln/detail/CVE-2020-36227

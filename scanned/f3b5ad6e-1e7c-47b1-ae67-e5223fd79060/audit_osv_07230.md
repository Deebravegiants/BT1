# [H] BIT-openldap-2020-25709

## Summary
Severity: High
Advisory: BIT-openldap-2020-25709
Aliases: CVE-2020-25709
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-25709
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.56

## Details
A flaw was found in OpenLDAP. This flaw allows an attacker who can send a malicious packet to be processed by OpenLDAP’s slapd server, to trigger an assertion failure. The highest threat from this vulnerability is to system availability.

## References
- http://seclists.org/fulldisclosure/2021/Feb/14
- https://bugzilla.redhat.com/show_bug.cgi?id=1899675
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00008.html
- https://security.netapp.com/advisory/ntap-20210716-0003/
- https://support.apple.com/kb/HT212147
- https://www.debian.org/security/2020/dsa-4792
- https://nvd.nist.gov/vuln/detail/CVE-2020-25709

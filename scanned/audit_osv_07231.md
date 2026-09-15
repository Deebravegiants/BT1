# [H] BIT-openldap-2020-25710

## Summary
Severity: High
Advisory: BIT-openldap-2020-25710
Aliases: CVE-2020-25710
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-25710
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.56

## Details
A flaw was found in OpenLDAP in versions before 2.4.56. This flaw allows an attacker who sends a malicious packet processed by OpenLDAP to force a failed assertion in csnNormalize23(). The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1899678
- https://git.openldap.org/openldap/openldap/-/commit/ab3915154e69920d480205b4bf5ccb2b391a0a1f#a2feb6ed0257c21c6672793ee2f94eaadc10c72c
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00008.html
- https://security.netapp.com/advisory/ntap-20210716-0003/
- https://www.debian.org/security/2020/dsa-4792
- https://nvd.nist.gov/vuln/detail/CVE-2020-25710

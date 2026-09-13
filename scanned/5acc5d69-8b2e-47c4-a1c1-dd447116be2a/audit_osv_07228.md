# [M] BIT-openldap-2020-15719

## Summary
Severity: Medium
Advisory: BIT-openldap-2020-15719
Aliases: CVE-2020-15719
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-15719
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.46-10.el8

## Details
libldap in certain third-party OpenLDAP packages has a certificate-validation flaw when the third-party package is asserting RFC6125 support. It considers CN even when there is a non-matching subjectAltName (SAN). This is fixed in, for example, openldap-2.4.46-10.el8 in Red Hat Enterprise Linux.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00059.html
- https://access.redhat.com/errata/RHBA-2019:3674
- https://bugs.openldap.org/show_bug.cgi?id=9266
- https://bugzilla.redhat.com/show_bug.cgi?id=1740070
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-15719

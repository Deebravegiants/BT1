# [H] BIT-openldap-2020-12243

## Summary
Severity: High
Advisory: BIT-openldap-2020-12243
Aliases: CVE-2020-12243
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-12243
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.50

## Details
In filter.c in slapd in OpenLDAP before 2.4.50, LDAP search filters with nested boolean expressions can result in denial of service (daemon crash).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00016.html
- https://bugs.openldap.org/show_bug.cgi?id=9202
- https://git.openldap.org/openldap/openldap/-/blob/OPENLDAP_REL_ENG_2_4/CHANGES
- https://git.openldap.org/openldap/openldap/-/commit/98464c11df8247d6a11b52e294ba5dd4f0380440
- https://lists.debian.org/debian-lts-announce/2020/05/msg00001.html
- https://security.netapp.com/advisory/ntap-20200511-0003/
- https://support.apple.com/kb/HT211289
- https://usn.ubuntu.com/4352-1/
- https://usn.ubuntu.com/4352-2/
- https://www.debian.org/security/2020/dsa-4666
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-12243

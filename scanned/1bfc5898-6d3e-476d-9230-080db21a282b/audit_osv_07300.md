# [H] BIT-postgresql-2020-14349

## Summary
Severity: High
Advisory: BIT-postgresql-2020-14349
Aliases: CVE-2020-14349
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2020-14349
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=12.0.0 <12.4.0

## Details
It was found that PostgreSQL versions before 12.4, before 11.9 and before 10.14 did not properly sanitize the search_path during logical replication. An authenticated attacker could use this flaw in an attack similar to CVE-2018-1058, in order to execute arbitrary SQL command in the context of the user used for replication.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00008.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1865744
- https://security.gentoo.org/glsa/202008-13
- https://security.netapp.com/advisory/ntap-20200918-0002/
- https://usn.ubuntu.com/4472-1/
- https://nvd.nist.gov/vuln/detail/CVE-2020-14349

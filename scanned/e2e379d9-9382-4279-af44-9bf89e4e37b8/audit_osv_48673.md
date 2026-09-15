# [H] CVE-2018-10925

## Summary
Severity: High
Advisory: CVE-2018-10925
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-08-09
Source: https://osv.dev/vulnerability/CVE-2018-10925
Type: osv

## Details
It was discovered that PostgreSQL versions before 10.5, 9.6.10, 9.5.14, 9.4.19, and 9.3.24 failed to properly check authorization on certain statements involved with "INSERT ... ON CONFLICT DO UPDATE". An attacker with "CREATE TABLE" privileges could exploit this to read arbitrary bytes server memory. If the attacker also had certain "INSERT" and limited "UPDATE" privileges to a particular table, they could exploit this to update other columns in the same table.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- https://access.redhat.com/errata/RHSA-2018:2511
- https://access.redhat.com/errata/RHSA-2018:3816
- https://www.debian.org/security/2018/dsa-4269
- https://www.postgresql.org/about/news/1878/
- http://www.securityfocus.com/bid/105052
- http://www.securitytracker.com/id/1041446
- https://access.redhat.com/errata/RHSA-2018:2565
- https://access.redhat.com/errata/RHSA-2018:2566
- https://security.gentoo.org/glsa/201810-08
- https://usn.ubuntu.com/3744-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10925

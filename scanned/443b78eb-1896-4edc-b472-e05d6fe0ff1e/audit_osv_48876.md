# [C] CVE-2018-16850

## Summary
Severity: Critical
Advisory: CVE-2018-16850
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-13
Source: https://osv.dev/vulnerability/CVE-2018-16850
Type: osv

## Details
postgresql before versions 11.1, 10.6 is vulnerable to a to SQL injection in pg_upgrade and pg_dump via CREATE TRIGGER ... REFERENCING. Using a purpose-crafted trigger definition, an attacker can cause arbitrary SQL statements to run, with superuser privileges.

## References
- https://usn.ubuntu.com/3818-1/
- https://www.postgresql.org/about/news/1905/
- http://www.securityfocus.com/bid/105923
- http://www.securitytracker.com/id/1042144
- https://access.redhat.com/errata/RHSA-2018:3757
- https://security.gentoo.org/glsa/201811-24
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16850

# [C] CVE-2018-1115

## Summary
Severity: Critical
Advisory: CVE-2018-1115
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-1115
Type: osv

## Details
postgresql before versions 10.4, 9.6.9 is vulnerable in the adminpack extension, the pg_catalog.pg_logfile_rotate() function doesn't follow the same ACLs than pg_rorate_logfile. If the adminpack is added to a database, an attacker able to connect to it could exploit this to force log rotation.

## References
- https://git.postgresql.org/gitweb/?p=postgresql.git%3Ba=commitdiff%3Bh=7b34740
- https://security.gentoo.org/glsa/201810-08
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- http://www.securityfocus.com/bid/104285
- https://access.redhat.com/errata/RHSA-2018:2565
- https://access.redhat.com/errata/RHSA-2018:2566
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1115

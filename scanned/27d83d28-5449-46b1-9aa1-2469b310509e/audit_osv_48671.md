# [H] CVE-2018-10915

## Summary
Severity: High
Advisory: CVE-2018-10915
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-09
Source: https://osv.dev/vulnerability/CVE-2018-10915
Type: osv

## Details
A vulnerability was found in libpq, the default PostgreSQL client library where libpq failed to properly reset its internal state between connections. If an affected version of libpq was used with "host" or "hostaddr" connection parameters from untrusted input, attackers could bypass client-side connection security features, obtain access to higher privileged connections or potentially cause other impact through SQL injection, by causing the PQescape() functions to malfunction. Postgresql versions before 10.5, 9.6.10, 9.5.14, 9.4.19, and 9.3.24 are affected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- https://access.redhat.com/errata/RHSA-2018:2511
- https://access.redhat.com/errata/RHSA-2018:2557
- https://access.redhat.com/errata/RHSA-2018:2721
- https://access.redhat.com/errata/RHSA-2018:3816
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2018:2729
- https://security.gentoo.org/glsa/201810-08
- https://usn.ubuntu.com/3744-1/
- https://www.debian.org/security/2018/dsa-4269
- http://www.securitytracker.com/id/1041446
- https://access.redhat.com/errata/RHSA-2018:2565
- https://www.postgresql.org/about/news/1878/
- http://www.securityfocus.com/bid/105054
- https://access.redhat.com/errata/RHSA-2018:2566
- https://lists.debian.org/debian-lts-announce/2018/08/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10915

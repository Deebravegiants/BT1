# [M] CVE-2017-15099

## Summary
Severity: Medium
Advisory: CVE-2017-15099
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-15099
Type: osv

## Details
INSERT ... ON CONFLICT DO UPDATE commands in PostgreSQL 10.x before 10.1, 9.6.x before 9.6.6, and 9.5.x before 9.5.10 disclose table contents that the invoker lacks privilege to read. These exploits affect only tables where the attacker lacks full read access but has both INSERT and UPDATE privileges. Exploits bypass row level security policies and lack of SELECT privilege.

## References
- http://www.securityfocus.com/bid/101781
- http://www.securitytracker.com/id/1039752
- https://access.redhat.com/errata/RHSA-2018:2511
- https://access.redhat.com/errata/RHSA-2018:2566
- https://www.debian.org/security/2017/dsa-4028
- https://www.postgresql.org/about/news/1801/
- https://www.postgresql.org/support/security/

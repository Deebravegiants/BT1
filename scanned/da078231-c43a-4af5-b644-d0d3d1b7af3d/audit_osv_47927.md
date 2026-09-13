# [H] CVE-2017-15098

## Summary
Severity: High
Advisory: CVE-2017-15098
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-15098
Type: osv

## Details
Invalid json_populate_recordset or jsonb_populate_recordset function calls in PostgreSQL 10.x before 10.1, 9.6.x before 9.6.6, 9.5.x before 9.5.10, 9.4.x before 9.4.15, and 9.3.x before 9.3.20 can crash the server or disclose a few bytes of server memory.

## References
- http://www.securityfocus.com/bid/101781
- http://www.securitytracker.com/id/1039752
- https://access.redhat.com/errata/RHSA-2018:2511
- https://access.redhat.com/errata/RHSA-2018:2566
- https://www.debian.org/security/2017/dsa-4027
- https://www.debian.org/security/2017/dsa-4028
- https://www.postgresql.org/about/news/1801/
- https://www.postgresql.org/support/security/

# [M] CVE-2019-10130

## Summary
Severity: Medium
Advisory: CVE-2019-10130
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10130
Type: osv

## Details
A vulnerability was found in PostgreSQL versions 11.x up to excluding 11.3, 10.x up to excluding 10.8, 9.6.x up to, excluding 9.6.13, 9.5.x up to, excluding 9.5.17. PostgreSQL maintains column statistics for tables. Certain statistics, such as histograms and lists of most common values, contain values taken from the column. PostgreSQL does not evaluate row security policies before consulting those statistics during query planning; an attacker can exploit this to read the most common values of certain columns. Affected columns are those for which the attacker has SELECT privilege and for which, in an ordinary query, row-level security prunes the set of rows visible to the attacker.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- https://security.gentoo.org/glsa/202003-03
- https://www.postgresql.org/about/news/1939/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10130

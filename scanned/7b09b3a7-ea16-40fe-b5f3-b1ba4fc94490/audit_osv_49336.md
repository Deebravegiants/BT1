# [H] CVE-2019-10208

## Summary
Severity: High
Advisory: CVE-2019-10208
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-10208
Type: osv

## Details
A flaw was discovered in postgresql versions 9.4.x before 9.4.24, 9.5.x before 9.5.19, 9.6.x before 9.6.15, 10.x before 10.10 and 11.x before 11.5 where arbitrary SQL statements can be executed given a suitable SECURITY DEFINER function. An attacker, with EXECUTE permission on the function, can execute arbitrary SQL as the owner of the function.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- https://www.postgresql.org/about/news/1960/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10208

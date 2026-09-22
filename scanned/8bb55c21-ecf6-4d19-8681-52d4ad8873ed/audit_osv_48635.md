# [M] CVE-2018-1052

## Summary
Severity: Medium
Advisory: CVE-2018-1052
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1052
Type: osv

## Details
Memory disclosure vulnerability in table partitioning was found in postgresql 10.x before 10.2, allowing an authenticated attacker to read arbitrary bytes of server memory via purpose-crafted insert to a partitioned table.

## References
- http://www.securityfocus.com/bid/102987
- https://www.postgresql.org/about/news/1829/

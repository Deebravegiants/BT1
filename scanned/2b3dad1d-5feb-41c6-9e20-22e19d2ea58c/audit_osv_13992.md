# [H] CVE-2018-6196

## Summary
Severity: High
Advisory: CVE-2018-6196
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/CVE-2018-6196
Type: osv

## Details
w3m through 0.5.3 is prone to an infinite recursion flaw in HTMLlineproc0 because the feed_table_block_tag function in table.c does not prevent a negative indent value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/04/msg00025.html
- https://usn.ubuntu.com/3555-1/
- https://usn.ubuntu.com/3555-2/
- https://github.com/tats/w3m/commit/8354763b90490d4105695df52674d0fcef823e92
- https://github.com/tats/w3m/issues/88

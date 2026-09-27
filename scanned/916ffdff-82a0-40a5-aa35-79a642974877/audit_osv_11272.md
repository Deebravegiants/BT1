# [H] CVE-2017-7177

## Summary
Severity: High
Advisory: CVE-2017-7177
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-18
Source: https://osv.dev/vulnerability/CVE-2017-7177
Type: osv

## Details
Suricata before 3.2.1 has an IPv4 defragmentation evasion issue caused by lack of a check for the IP protocol during fragment matching.

## References
- http://www.securityfocus.com/bid/97047
- https://lists.debian.org/debian-lts-announce/2018/12/msg00000.html
- https://github.com/inliniac/suricata/commit/4a04f814b15762eb446a5ead4d69d021512df6f8
- https://redmine.openinfosecfoundation.org/issues/2019

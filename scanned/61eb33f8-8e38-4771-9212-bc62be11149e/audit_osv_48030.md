# [H] CVE-2017-17459

## Summary
Severity: High
Advisory: CVE-2017-17459
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-17459
Type: osv

## Details
http_transport.c in Fossil before 2.4, when the SSH sync protocol is used, allows user-assisted remote attackers to execute arbitrary commands via an ssh URL with an initial dash character in the hostname, a related issue to CVE-2017-9800, CVE-2017-12836, CVE-2017-12976, CVE-2017-14176, CVE-2017-16228, CVE-2017-1000116, and CVE-2017-1000117.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BLAFCQGE7C5UMX75LESNUMKTXTURUVQM/
- https://www.fossil-scm.org/xfer/doc/trunk/www/changes.wiki#v2_4
- https://bugzilla.opensuse.org/show_bug.cgi?id=1071709
- https://www.fossil-scm.org/xfer/info/1f63db591c77108c

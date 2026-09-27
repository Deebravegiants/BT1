# [H] CVE-2018-8740

## Summary
Severity: High
Advisory: CVE-2018-8740
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-17
Source: https://osv.dev/vulnerability/CVE-2018-8740
Type: osv

## Details
In SQLite through 3.22.0, databases whose schema is corrupted using a CREATE TABLE AS statement could cause a NULL pointer dereference, related to build.c and prepare.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00050.html
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU4NZ6DDU4BEM3ACM3FM6GLEPX56ZQXK/
- https://usn.ubuntu.com/4205-1/
- https://usn.ubuntu.com/4394-1/
- http://www.securityfocus.com/bid/103466
- https://bugs.launchpad.net/ubuntu/+source/sqlite3/+bug/1756349
- https://lists.debian.org/debian-lts-announce/2019/01/msg00009.html
- https://www.sqlite.org/cgi/src/timeline?r=corrupt-schema
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=6964
- https://www.sqlite.org/cgi/src/vdiff?from=1774f1c3baf0bc3d&to=d75e67654aa9620b

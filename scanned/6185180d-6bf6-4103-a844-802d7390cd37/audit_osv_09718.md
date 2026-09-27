# [C] CVE-2017-10989

## Summary
Severity: Critical
Advisory: CVE-2017-10989
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-10989
Type: osv

## Details
The getNodeSize function in ext/rtree/rtree.c in SQLite through 3.19.3, as used in GDAL and other products, mishandles undersized RTree blobs in a crafted database, leading to a heap-based buffer over-read or possibly unspecified other impact.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00050.html
- http://www.securitytracker.com/id/1039427
- https://lists.debian.org/debian-lts-announce/2019/01/msg00009.html
- https://support.apple.com/HT208112
- https://support.apple.com/HT208113
- https://support.apple.com/HT208115
- https://support.apple.com/HT208144
- https://usn.ubuntu.com/4019-1/
- https://usn.ubuntu.com/4019-2/
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/99502
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=2405
- http://marc.info/?l=sqlite-users&m=149933696214713&w=2
- https://bugs.launchpad.net/ubuntu/+source/sqlite3/+bug/1700937
- https://sqlite.org/src/info/66de6f4a
- https://sqlite.org/src/vpatch?from=0db20efe201736b3&to=66de6f4a9504ec26

# [H] CVE-2019-9937

## Summary
Severity: High
Advisory: CVE-2019-9937
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-22
Source: https://osv.dev/vulnerability/CVE-2019-9937
Type: osv

## Details
In SQLite 3.27.2, interleaving reads and writes in a single transaction with an fts5 virtual table will lead to a NULL Pointer Dereference in fts5ChunkIterate in sqlite3.c. This is related to ext/fts5/fts5_hash.c and ext/fts5/fts5_index.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00026.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXD2GYJVTDGEQPUNMMMC5TB7MQXOBBMO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N66U5PY5UJU4XBFZJH7QNKIDNAVIB4OP/
- https://usn.ubuntu.com/4019-1/
- https://www.mail-archive.com/sqlite-users%40mailinglists.sqlite.org/msg114383.html
- https://www.mail-archive.com/sqlite-users%40mailinglists.sqlite.org/msg114393.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://www.securityfocus.com/bid/107562
- https://security.gentoo.org/glsa/201908-09
- https://security.netapp.com/advisory/ntap-20190416-0005/
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://sqlite.org/src/info/45c73deb440496e8

# [H] CVE-2021-33582

## Summary
Severity: High
Advisory: CVE-2021-33582
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-01
Source: https://osv.dev/vulnerability/CVE-2021-33582
Type: osv

## Details
Cyrus IMAP before 3.4.2 allows remote attackers to cause a denial of service (multiple-minute daemon hang) via input that is mishandled during hash-table interaction. Because there are many insertions into a single bucket, strcmp becomes slow. This is fixed in 3.4.2, 3.2.8, and 3.0.16.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6HEO3RURJW6NLIXS7NK5PVU6MGHC4SCM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJZB45QBUN7CZFGOWCZYUYACNBTX7LVS/
- https://github.com/cyrusimap/cyrus-imapd/security/advisories
- https://lists.debian.org/debian-lts-announce/2022/06/msg00013.html
- https://cyrus.topicbox.com/groups/announce/T3dde0a2352462975-M1386fc44adf967e072f8df13/cyrus-imap-3-4-2-3-2-8-and-3-0-16-released
- https://github.com/cyrusimap/cyrus-imapd/commits/master
- https://www.cyrusimap.org/imap/download/release-notes/index.html

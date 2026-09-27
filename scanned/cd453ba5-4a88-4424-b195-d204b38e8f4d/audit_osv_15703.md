# [C] CVE-2019-18928

## Summary
Severity: Critical
Advisory: CVE-2019-18928
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/CVE-2019-18928
Type: osv

## Details
Cyrus IMAP 2.5.x before 2.5.14 and 3.x before 3.0.12 allows privilege escalation because an HTTP request may be interpreted in the authentication context of an unrelated previous request that arrived over the same connection.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LAGKPZDXQ6KRUGQVRAO6N4PCINP6KS5F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PHV3TUU53WCKJ3BBRK2EHAF44MSZEFK6/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00013.html
- https://www.cyrusimap.org/imap/download/release-notes/2.5/x/2.5.14.html
- https://www.cyrusimap.org/imap/download/release-notes/3.0/x/3.0.12.html

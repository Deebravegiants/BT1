# [H] CVE-2021-20247

## Summary
Severity: High
Advisory: CVE-2021-20247
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-20247
Type: osv

## Details
A flaw was found in mbsync before v1.3.5 and v1.4.1. Validations of the mailbox names returned by IMAP LIST/LSUB do not occur allowing a malicious or compromised server to use specially crafted mailbox names containing '..' path components to access data outside the designated mailbox on the opposite end of the synchronization channel. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CAXQLCK35QGRCRENRTGKJO4VVZGUXUJJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GVDEBZQJMWDW5JFK4NTHH6DAFNAZTESW/
- https://lists.debian.org/debian-lts-announce/2022/07/msg00001.html
- https://security.gentoo.org/glsa/202208-15
- https://bugzilla.redhat.com/show_bug.cgi?id=1928963
- https://www.openwall.com/lists/oss-security/2021/02/22/1

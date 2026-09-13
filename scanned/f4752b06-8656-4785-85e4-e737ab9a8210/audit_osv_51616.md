# [H] CVE-2021-3578

## Summary
Severity: High
Advisory: CVE-2021-3578
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3578
Type: osv

## Details
A flaw was found in mbsync before v1.3.6 and v1.4.2, where an unchecked pointer cast allows a malicious or compromised server to write an arbitrary integer value past the end of a heap-allocated structure by issuing an unexpected APPENDUID response. This could be plausibly exploited for remote code execution on the client.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RPIDLIJKNRJHUVBCL7QGAPAAVPIHQGXK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U75UFEWRAZYKVL5NHMPBUOLWN3WXTOEI/
- https://lists.debian.org/debian-lts-announce/2022/07/msg00001.html
- https://security.gentoo.org/glsa/202208-15
- https://bugzilla.redhat.com/show_bug.cgi?id=1961710
- https://www.openwall.com/lists/oss-security/2021/06/07/1
- http://www.openwall.com/lists/oss-security/2021/06/07/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1967397
- https://github.blog/2021-06-10-privilege-escalation-polkit-root-on-linux-with-bug/

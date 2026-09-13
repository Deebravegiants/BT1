# [H] CVE-2019-10131

## Summary
Severity: High
Advisory: CVE-2019-10131
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2019-10131
Type: osv

## Details
An off-by-one read vulnerability was discovered in ImageMagick before version 7.0.7-28 in the formatIPTCfromBuffer function in coders/meta.c. A local attacker may use this flaw to read beyond the end of the buffer or to crash the program.

## References
- http://www.securityfocus.com/bid/108117
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4034-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10131
- https://github.com/ImageMagick/ImageMagick/commit/cb1214c124e1bd61f7dd551b94a794864861592e

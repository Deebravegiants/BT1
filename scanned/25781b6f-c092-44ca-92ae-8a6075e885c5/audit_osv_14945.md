# [M] CVE-2019-12521

## Summary
Severity: Medium
Advisory: CVE-2019-12521
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2019-12521
Type: osv

## Details
An issue was discovered in Squid through 4.7. When Squid is parsing ESI, it keeps the ESI elements in ESIContext. ESIContext contains a buffer for holding a stack of ESIElements. When a new ESIElement is parsed, it is added via addStackElement. addStackElement has a check for the number of elements in this buffer, but it's off by 1, leading to a Heap Overflow of 1 element. The overflow is within the same structure so it can't affect adjacent memory blocks, and thus just leads to a crash while processing.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00018.html
- https://gitlab.com/jeriko.one/security/-/blob/master/squid/CVEs/CVE-2019-12521.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.gentoo.org/glsa/202005-05
- https://security.netapp.com/advisory/ntap-20210205-0006/
- https://usn.ubuntu.com/4356-1/
- https://www.debian.org/security/2020/dsa-4682
- http://www.openwall.com/lists/oss-security/2020/04/23/1

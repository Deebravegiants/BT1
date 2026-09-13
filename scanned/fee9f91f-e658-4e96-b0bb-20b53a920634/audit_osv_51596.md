# [H] CVE-2021-3483

## Summary
Severity: High
Advisory: CVE-2021-3483
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2021-3483
Type: osv

## Details
A flaw was found in the Nosy driver in the Linux kernel. This issue allows a device to be inserted twice into a doubly-linked list, leading to a use-after-free when one of these devices is removed. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability. Versions before kernel 5.12-rc6 are affected

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://security.netapp.com/advisory/ntap-20210629-0002/
- http://www.openwall.com/lists/oss-security/2021/04/07/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1948045

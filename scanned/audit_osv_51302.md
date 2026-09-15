# [M] CVE-2021-28038

## Summary
Severity: Medium
Advisory: CVE-2021-28038
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-28038
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.3, as used with Xen PV. A certain part of the netback driver lacks necessary treatment of errors such as failed memory allocations (as a result of changes to the handling of grant mapping errors). A host OS denial of service may occur during misbehavior of a networking frontend driver. NOTE: this issue exists because of an incomplete fix for CVE-2021-26931.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2991397d23ec597405b116d96de3813420bdcbc3
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://security.netapp.com/advisory/ntap-20210409-0001/
- http://xenbits.xen.org/xsa/advisory-367.html
- http://www.openwall.com/lists/oss-security/2021/03/05/1

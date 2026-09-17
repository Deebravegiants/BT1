# [M] CVE-2020-25285

## Summary
Severity: Medium
Advisory: CVE-2020-25285
Aliases: A-168881044, PUB-A-168881044
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-13
Source: https://osv.dev/vulnerability/CVE-2020-25285
Type: osv

## Details
A race condition between hugetlb sysctl handlers in mm/hugetlb.c in the Linux kernel before 5.8.8 could be used by local attackers to corrupt memory, cause a NULL pointer dereference, or possibly have unspecified other impact, aka CID-17743798d812.

## References
- https://usn.ubuntu.com/4576-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.8
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://security.netapp.com/advisory/ntap-20201009-0002/
- https://usn.ubuntu.com/4579-1/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://twitter.com/grsecurity/status/1303749848898904067
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=17743798d81238ab13050e8e2833699b54e15467

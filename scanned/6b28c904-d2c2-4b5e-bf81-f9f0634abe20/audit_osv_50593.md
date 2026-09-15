# [M] CVE-2020-25284

## Summary
Severity: Medium
Advisory: CVE-2020-25284
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-13
Source: https://osv.dev/vulnerability/CVE-2020-25284
Type: osv

## Details
The rbd block device driver in drivers/block/rbd.c in the Linux kernel through 5.8.9 used incomplete permission checking for access to rbd devices, which could be leveraged by local attackers to map or unmap rbd block devices, aka CID-f44d04e696fe.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://twitter.com/grsecurity/status/1304537507560919041
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f44d04e696feaf13d192d942c4f14ad2e117065a

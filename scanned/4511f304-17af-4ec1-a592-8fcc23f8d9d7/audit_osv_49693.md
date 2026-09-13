# [M] CVE-2019-16232

## Summary
Severity: Medium
Advisory: CVE-2019-16232
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16232
Type: osv

## Details
drivers/net/wireless/marvell/libertas/if_sdio.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://usn.ubuntu.com/4287-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00010.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4287-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00064.html
- https://usn.ubuntu.com/4284-1/
- https://lkml.org/lkml/2019/9/9/487

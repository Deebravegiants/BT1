# [H] CVE-2020-25669

## Summary
Severity: High
Advisory: CVE-2020-25669
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-25669
Type: osv

## Details
A vulnerability was found in the Linux Kernel where the function sunkbd_reinit having been scheduled by sunkbd_interrupt before sunkbd being freed. Though the dangling pointer is set to NULL in sunkbd_disconnect, there is still an alias in sunkbd_reinit causing Use After Free.

## References
- https://www.openwall.com/lists/oss-security/2020/11/20/5%2C
- https://www.openwall.com/lists/oss-security/2020/11/05/2%2C
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://security.netapp.com/advisory/ntap-20210702-0006/
- https://github.com/torvalds/linux/commit/77e70d351db7de07a46ac49b87a6c3c7a60fca7e
- http://www.openwall.com/lists/oss-security/2020/11/05/2
- http://www.openwall.com/lists/oss-security/2020/11/20/5

# [M] CVE-2021-31916

## Summary
Severity: Medium
Advisory: CVE-2021-31916
Aliases: A-187955767, PUB-A-187955767
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-31916
Type: osv

## Details
An out-of-bounds (OOB) memory write flaw was found in list_devices in drivers/md/dm-ioctl.c in the Multi-device driver module in the Linux kernel before 5.12. A bound check failure allows an attacker with special user (CAP_SYS_ADMIN) privilege to gain access to out-of-bounds memory leading to a system crash or a leak of internal kernel information. The highest threat from this vulnerability is to system availability.

## References
- https://seclists.org/oss-sec/2021/q1/268
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1946965
- https://github.com/torvalds/linux/commit/4edbe1d7bcffcd6269f3b5eb63f710393ff2ec7a

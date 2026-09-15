# [M] CVE-2021-3753

## Summary
Severity: Medium
Advisory: CVE-2021-3753
Aliases: A-222023207, PUB-A-222023207
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3753
Type: osv

## Details
A race problem was seen in the vt_k_ioctl in drivers/tty/vt/vt_ioctl.c in the Linux kernel, which may cause an out of bounds read in vt as the write access to vc_mode is not protected by lock-in vt_ioctl (KDSETMDE). The highest threat from this vulnerability is to data confidentiality.

## References
- https://security.netapp.com/advisory/ntap-20221028-0003/
- https://www.openwall.com/lists/oss-security/2021/09/01/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1999589
- https://github.com/torvalds/linux/commit/2287a51ba822384834dafc1c798453375d1107c7

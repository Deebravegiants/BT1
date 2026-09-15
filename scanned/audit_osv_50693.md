# [M] CVE-2020-28974

## Summary
Severity: Medium
Advisory: CVE-2020-28974
CVSS: 5.0 (CVSS:3.1/AV:P/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-11-20
Source: https://osv.dev/vulnerability/CVE-2020-28974
Type: osv

## Details
A slab-out-of-bounds read in fbcon in the Linux kernel before 5.9.7 could be used by local attackers to read privileged information or potentially crash the kernel, aka CID-3c4e0dff2095. This occurs because KD_FONT_OP_COPY in drivers/tty/vt/vt.c can be used for manipulations such as font height.

## References
- https://security.netapp.com/advisory/ntap-20210108-0003/
- http://www.openwall.com/lists/oss-security/2020/11/25/1
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.7
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3c4e0dff2095c579b142d5a0693257f1c58b4804
- https://seclists.org/oss-sec/2020/q4/104

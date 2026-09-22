# [H] CVE-2022-3424

## Summary
Severity: High
Advisory: CVE-2022-3424
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-3424
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s SGI GRU driver in the way the first gru_file_unlocked_ioctl function is called by the user, where a fail pass occurs in the gru_check_chiplet_assignment function. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://lore.kernel.org/all/20221019031445.901570-1-zyytlz.wz%40163.com/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20230406-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2132640
- https://github.com/torvalds/linux/commit/643a16a0eb1d6ac23744bb6e90a00fc21148a9dc
- https://www.spinics.net/lists/kernel/msg4518970.html

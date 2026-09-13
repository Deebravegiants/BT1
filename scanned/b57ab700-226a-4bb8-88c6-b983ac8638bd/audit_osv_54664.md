# [M] CVE-2024-25739

## Summary
Severity: Medium
Advisory: CVE-2024-25739
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2024-25739
Type: osv

## Details
create_empty_lvol in drivers/mtd/ubi/vtbl.c in the Linux kernel through 6.7.4 can attempt to allocate zero bytes, and crash, because of a missing check for ubi->leb_size.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=68a24aba7c593eafa8fd00f2f76407b9b32b47a9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://web.git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/drivers/mtd/ubi/vtbl.c?h=v6.6.24&id=d1b505c988b7
- https://groups.google.com/g/syzkaller/c/Xl97YcQA4hg
- https://www.spinics.net/lists/kernel/msg5074816.html

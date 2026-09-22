# [H] CVE-2018-16276

## Summary
Severity: High
Advisory: CVE-2018-16276
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-31
Source: https://osv.dev/vulnerability/CVE-2018-16276
Type: osv

## Details
An issue was discovered in yurex_read in drivers/usb/misc/yurex.c in the Linux kernel before 4.17.7. Local attackers could use user access read/writes with incorrect bounds checking in the yurex USB driver to crash the kernel or potentially escalate privileges.

## References
- https://usn.ubuntu.com/3847-3/
- https://www.debian.org/security/2018/dsa-4308
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3847-2/
- https://usn.ubuntu.com/3849-1/
- https://usn.ubuntu.com/3849-2/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.7
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3847-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1106095
- https://bugzilla.suse.com/show_bug.cgi?id=1115593
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f1e255d60ae66a9f672ff9a207ee6cd8e33d2679
- https://github.com/torvalds/linux/commit/f1e255d60ae66a9f672ff9a207ee6cd8e33d2679

# [M] CVE-2018-15572

## Summary
Severity: Medium
Advisory: CVE-2018-15572
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-15572
Type: osv

## Details
The spectre_v2_select_mitigation function in arch/x86/kernel/cpu/bugs.c in the Linux kernel before 4.18.1 does not always fill RSB upon a context switch, which makes it easier for attackers to conduct userspace-userspace spectreRSB attacks.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-1/
- https://usn.ubuntu.com/3777-3/
- https://www.debian.org/security/2018/dsa-4308
- https://usn.ubuntu.com/3775-1/
- https://usn.ubuntu.com/3775-2/
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3777-2/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=fdf82a7856b32d905c39afc85e34364491e46346
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.1
- https://github.com/torvalds/linux/commit/fdf82a7856b32d905c39afc85e34364491e46346

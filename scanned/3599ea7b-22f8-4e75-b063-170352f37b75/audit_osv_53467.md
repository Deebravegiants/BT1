# [M] CVE-2022-44034

## Summary
Severity: Medium
Advisory: CVE-2022-44034
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-30
Source: https://osv.dev/vulnerability/CVE-2022-44034
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.6. drivers/char/pcmcia/scr24x_cs.c has a race condition and resultant use-after-free if a physically proximate attacker removes a PCMCIA device while calling open(), aka a race condition between scr24x_open() and scr24x_remove().

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9b12f050c76f090cc6d0aebe0ef76fed79ec3f15
- https://lore.kernel.org/lkml/20220916050333.GA188358%40ubuntu/
- https://lore.kernel.org/lkml/20220919101825.GA313940%40ubuntu/

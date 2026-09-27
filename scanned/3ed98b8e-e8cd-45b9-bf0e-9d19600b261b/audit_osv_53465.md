# [M] CVE-2022-44032

## Summary
Severity: Medium
Advisory: CVE-2022-44032
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-30
Source: https://osv.dev/vulnerability/CVE-2022-44032
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.6. drivers/char/pcmcia/cm4000_cs.c has a race condition and resultant use-after-free if a physically proximate attacker removes a PCMCIA device while calling open(), aka a race condition between cmm_open() and cm4000_detach().

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9b12f050c76f090cc6d0aebe0ef76fed79ec3f15
- https://lore.kernel.org/lkml/20220915020834.GA110086%40ubuntu/
- https://lore.kernel.org/lkml/20220919040701.GA302806%40ubuntu/

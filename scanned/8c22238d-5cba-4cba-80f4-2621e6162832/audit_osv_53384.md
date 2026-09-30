# [M] CVE-2022-41848

## Summary
Severity: Medium
Advisory: CVE-2022-41848
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-30
Source: https://osv.dev/vulnerability/CVE-2022-41848
Type: osv

## Details
drivers/char/pcmcia/synclink_cs.c in the Linux kernel through 5.19.12 has a race condition and resultant use-after-free if a physically proximate attacker removes a PCMCIA device while calling ioctl, aka a race condition between mgslpc_ioctl and mgslpc_detach.

## References
- https://lore.kernel.org/lkml/20220919040251.GA302541%40ubuntu/T/#rc85e751f467b3e6f9ccef92cfa7fb8a6cc50c270
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/char/pcmcia/synclink_cs.c

# [M] CVE-2022-25375

## Summary
Severity: Medium
Advisory: CVE-2022-25375
Aliases: A-162326603, ASB-A-162326603
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-20
Source: https://osv.dev/vulnerability/CVE-2022-25375
Type: osv

## Details
An issue was discovered in drivers/usb/gadget/function/rndis.c in the Linux kernel before 5.16.10. The RNDIS USB gadget lacks validation of the size of the RNDIS_MSG_SET command. Attackers can obtain sensitive information from kernel memory.

## References
- https://github.com/szymonh/rndis-co
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5092
- https://www.debian.org/security/2022/dsa-5096
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.10
- https://github.com/torvalds/linux/commit/38ea1eac7d88072bbffb630e2b3db83ca649b826
- http://www.openwall.com/lists/oss-security/2022/02/21/1

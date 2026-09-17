# [H] CVE-2019-17075

## Summary
Severity: High
Advisory: CVE-2019-17075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-01
Source: https://osv.dev/vulnerability/CVE-2019-17075
Type: osv

## Details
An issue was discovered in write_tpt_entry in drivers/infiniband/hw/cxgb4/mem.c in the Linux kernel through 5.3.2. The cxgb4 driver is directly calling dma_map_single (a DMA function) from a stack variable. This could allow an attacker to trigger a Denial of Service, exploitable if this driver is used on an architecture for which this stack/DMA interaction has security relevance.

## References
- https://lore.kernel.org/lkml/20191001165611.GA3542072%40kroah.com
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://usn.ubuntu.com/4210-1/
- https://usn.ubuntu.com/4211-1/
- https://usn.ubuntu.com/4211-2/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://seclists.org/bugtraq/2019/Nov/11
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4226-1/

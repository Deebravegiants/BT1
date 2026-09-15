# [M] CVE-2023-1990

## Summary
Severity: Medium
Advisory: CVE-2023-1990
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-1990
Type: osv

## Details
A use-after-free flaw was found in ndlc_remove in drivers/nfc/st-nci/ndlc.c in the Linux Kernel. This flaw could allow an attacker to crash the system due to a race problem.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lore.kernel.org/all/20230312160837.2040857-1-zyytlz.wz%40163.com/

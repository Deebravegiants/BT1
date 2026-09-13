# [M] CVE-2023-1859

## Summary
Severity: Medium
Advisory: CVE-2023-1859
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-1859
Type: osv

## Details
A use-after-free flaw was found in xen_9pfs_front_removet in net/9p/trans_xen.c in Xen transport for 9pfs in the Linux Kernel. This flaw could allow a local attacker to crash the system due to a race problem, possibly leading to a kernel information leak.

## References
- https://lore.kernel.org/all/20230313090002.3308025-1-zyytlz.wz%40163.com/

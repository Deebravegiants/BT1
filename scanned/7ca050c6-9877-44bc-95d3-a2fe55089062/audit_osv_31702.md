# [H] net: hns3: fixed hclge_fetch_pf_reg accesses bar space out of bounds issue

## Summary
Severity: High
Advisory: CVE-2025-21650
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21650
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: fixed hclge_fetch_pf_reg accesses bar space out of bounds issue

The TQP BAR space is divided into two segments. TQPs 0-1023 and TQPs
1024-1279 are in different BAR space addresses. However,
hclge_fetch_pf_reg does not distinguish the tqp space information when
reading the tqp space information. When the number of TQPs is greater
than 1024, access bar space overwriting occurs.
The problem of different segments has been considered during the
initialization of tqp.io_base. Therefore, tqp.io_base is directly used
when the queue is read in hclge_fetch_pf_reg.

The error message:

Unable to handle kernel paging request at virtual address ffff800037200000
pc : hclge_fetch_pf_reg+0x138/0x250 [hclge]
lr : hclge_get_regs+0x84/0x1d0 [hclge]
Call trace:
 hclge_fetch_pf_reg+0x138/0x250 [hclge]
 hclge_get_regs+0x84/0x1d0 [hclge]
 hns3_get_regs+0x2c/0x50 [hns3]
 ethtool_get_regs+0xf4/0x270
 dev_ethtool+0x674/0x8a0
 dev_ioctl+0x270/0x36c
 sock_do_ioctl+0x110/0x2a0
 sock_ioctl+0x2ac/0x530
 __arm64_sys_ioctl+0xa8/0x100
 invoke_syscall+0x4c/0x124
 el0_svc_common.constprop.0+0x140/0x15c
 do_el0_svc+0x30/0xd0
 el0_svc+0x1c/0x2c
 el0_sync_handler+0xb0/0xb4
 el0_sync+0x168/0x180

## References
- https://git.kernel.org/stable/c/0575baa733fc4219f230aef22d5bc35d922f1e9a
- https://git.kernel.org/stable/c/7997ddd46c54408bcba5e37fe18b4d832e45d4d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21650.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21650
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

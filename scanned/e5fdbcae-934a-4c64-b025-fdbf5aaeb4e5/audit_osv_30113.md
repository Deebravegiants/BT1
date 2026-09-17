# [H] xhci: tegra: fix checked USB2 port number

## Summary
Severity: High
Advisory: CVE-2024-50075
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50075
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xhci: tegra: fix checked USB2 port number

If USB virtualizatoin is enabled, USB2 ports are shared between all
Virtual Functions. The USB2 port number owned by an USB2 root hub in
a Virtual Function may be less than total USB2 phy number supported
by the Tegra XUSB controller.

Using total USB2 phy number as port number to check all PORTSC values
would cause invalid memory access.

[  116.923438] Unable to handle kernel paging request at virtual address 006c622f7665642f
...
[  117.213640] Call trace:
[  117.216783]  tegra_xusb_enter_elpg+0x23c/0x658
[  117.222021]  tegra_xusb_runtime_suspend+0x40/0x68
[  117.227260]  pm_generic_runtime_suspend+0x30/0x50
[  117.232847]  __rpm_callback+0x84/0x3c0
[  117.237038]  rpm_suspend+0x2dc/0x740
[  117.241229] pm_runtime_work+0xa0/0xb8
[  117.245769]  process_scheduled_works+0x24c/0x478
[  117.251007]  worker_thread+0x23c/0x328
[  117.255547]  kthread+0x104/0x1b0
[  117.259389]  ret_from_fork+0x10/0x20
[  117.263582] Code: 54000222 f9461ae8 f8747908 b4ffff48 (f9400100)

## References
- https://git.kernel.org/stable/c/7d381137cb6ecf558ef6698c7730ddd482d4c8f2
- https://git.kernel.org/stable/c/9c696bf4ab54c7cec81221887564305f0ceeac0a
- https://git.kernel.org/stable/c/c46555f14b71f95a447f5d49fc3f1f80a1472da2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50075.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

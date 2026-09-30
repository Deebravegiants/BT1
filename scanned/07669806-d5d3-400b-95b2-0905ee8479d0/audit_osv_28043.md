# [H] wifi: rtl8xxxu: add cancel_work_sync() for c2hcmd_work

## Summary
Severity: High
Advisory: CVE-2024-27052
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27052
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtl8xxxu: add cancel_work_sync() for c2hcmd_work

The workqueue might still be running, when the driver is stopped. To
avoid a use-after-free, call cancel_work_sync() in rtl8xxxu_stop().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1213acb478a7181cd73eeaf00db430f1e45b1361
- https://git.kernel.org/stable/c/156012667b85ca7305cb363790d3ae8519a6f41e
- https://git.kernel.org/stable/c/3518cea837de4d106efa84ddac18a07b6de1384e
- https://git.kernel.org/stable/c/58fe3bbddfec10c6b216096d8c0e517cd8463e3a
- https://git.kernel.org/stable/c/7059cdb69f8e1a2707dd1e2f363348b507ed7707
- https://git.kernel.org/stable/c/ac512507ac89c01ed6cd4ca53032f52cdb23ea59
- https://git.kernel.org/stable/c/dddedfa3b29a63c2ca4336663806a6128b8545b4
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27052.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27052
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

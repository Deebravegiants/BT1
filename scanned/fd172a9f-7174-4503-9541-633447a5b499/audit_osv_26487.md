# [M] driver: soc: xilinx: fix memory leak in xlnx_add_cb_for_notify_event()

## Summary
Severity: Medium
Advisory: CVE-2023-53267
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53267
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver: soc: xilinx: fix memory leak in xlnx_add_cb_for_notify_event()

The kfree() should be called when memory fails to be allocated for
cb_data in xlnx_add_cb_for_notify_event(), otherwise there will be
a memory leak, so add kfree() to fix it.

## References
- https://git.kernel.org/stable/c/1bea534991b9b35c41848a397666ada436456beb
- https://git.kernel.org/stable/c/9dfb6c784e385f6e61994bb4e16ce12f3e4940be
- https://git.kernel.org/stable/c/d35290addcbac94b076babe0a798a8c043421812
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53267.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53267
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

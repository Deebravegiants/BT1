# [M] ptdma: pt_core_execute_cmd() should use spinlock

## Summary
Severity: Medium
Advisory: CVE-2023-53013
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53013
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptdma: pt_core_execute_cmd() should use spinlock

The interrupt handler (pt_core_irq_handler()) of the ptdma
driver can be called from interrupt context. The code flow
in this function can lead down to pt_core_execute_cmd() which
will attempt to grab a mutex, which is not appropriate in
interrupt context and ultimately leads to a kernel panic.
The fix here changes this mutex to a spinlock, which has
been verified to resolve the issue.

## References
- https://git.kernel.org/stable/c/13ba563c2c8055ba8a637c9f70bb833b43cb4207
- https://git.kernel.org/stable/c/95e5fda3b5f9ed8239b145da3fa01e641cf5d53c
- https://git.kernel.org/stable/c/ed0d8f731e0bf1bb12a7a37698ac613db20e2794
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53013.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53013
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

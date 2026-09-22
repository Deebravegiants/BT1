# [M] genirq/ipi: Fix NULL pointer deref in irq_data_get_affinity_mask()

## Summary
Severity: Medium
Advisory: CVE-2023-53332
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53332
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

genirq/ipi: Fix NULL pointer deref in irq_data_get_affinity_mask()

If ipi_send_{mask|single}() is called with an invalid interrupt number, all
the local variables there will be NULL. ipi_send_verify() which is invoked
from these functions does verify its 'data' parameter, resulting in a
kernel oops in irq_data_get_affinity_mask() as the passed NULL pointer gets
dereferenced.

Add a missing NULL pointer check in ipi_send_verify()...

Found by Linux Verification Center (linuxtesting.org) with the SVACE static
analysis tool.

## References
- https://git.kernel.org/stable/c/7448c73d64075051f50caed2c62f46553b69ab8a
- https://git.kernel.org/stable/c/926aef60ea64cd9becf2829f7388f48dbe8bcb11
- https://git.kernel.org/stable/c/feabecaff5902f896531dde90646ca5dfa9d4f7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53332.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53332
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

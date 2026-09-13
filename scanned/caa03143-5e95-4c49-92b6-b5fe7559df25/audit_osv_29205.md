# [H] dmaengine: idxd: Fix possible Use-After-Free in irq_process_work_list

## Summary
Severity: High
Advisory: CVE-2024-40956
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40956
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: Fix possible Use-After-Free in irq_process_work_list

Use list_for_each_entry_safe() to allow iterating through the list and
deleting the entry in the iteration process. The descriptor is freed via
idxd_desc_complete() and there's a slight chance may cause issue for
the list iterator when the descriptor is reused by another thread
without it being deleted from the list.

## References
- https://git.kernel.org/stable/c/1b08bf5a17c66ab7dbb628df5344da53c8e7ab33
- https://git.kernel.org/stable/c/83163667d881100a485b6c2daa30301b7f68d9b5
- https://git.kernel.org/stable/c/a14968921486793f2a956086895c3793761309dd
- https://git.kernel.org/stable/c/e3215deca4520773cd2b155bed164c12365149a7
- https://git.kernel.org/stable/c/faa35db78b058a2ab6e074ee283f69fa398c36a8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40956.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

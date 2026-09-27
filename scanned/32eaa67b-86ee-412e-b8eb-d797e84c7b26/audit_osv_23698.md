# [M] ata: pata_octeon_cf: Fix refcount leak in octeon_cf_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49354
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49354
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: pata_octeon_cf: Fix refcount leak in octeon_cf_probe

of_find_device_by_node() takes reference, we should use put_device()
to release it when not need anymore.
Add missing put_device() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/10d6bdf532902be1d8aa5900b3c03c5671612aa2
- https://git.kernel.org/stable/c/19cb3ece14547cb1ca2021798aaf49a3f82643d1
- https://git.kernel.org/stable/c/7bd85c5ba1687daf54e3b6907673c3604b1e75cf
- https://git.kernel.org/stable/c/888312dc297a8a103f6371ef668c7e04f57a7679
- https://git.kernel.org/stable/c/8d8ad067b90f231b8fdb14acee673ca4012f6045
- https://git.kernel.org/stable/c/a4d3e5f1d7d4f8b5e3834fec0f057a762c55806b
- https://git.kernel.org/stable/c/c9782e1b21bee4b783a64b2a91e7e71406c21a21
- https://git.kernel.org/stable/c/d5a1e7f33c88780b279835d63665d7e38ccb671f
- https://git.kernel.org/stable/c/fb2cb409b504bb3a69e65a17f3120328c8e50219
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49354.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

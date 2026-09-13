# [M] PCI: endpoint: epf-mhi: Avoid NULL dereference if DT lacks 'mmio'

## Summary
Severity: Medium
Advisory: CVE-2024-56689
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56689
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: endpoint: epf-mhi: Avoid NULL dereference if DT lacks 'mmio'

If platform_get_resource_byname() fails and returns NULL because DT lacks
an 'mmio' property for the MHI endpoint, dereferencing res->start will
cause a NULL pointer access. Add a check to prevent it.

[kwilczynski: error message update per the review feedback]
[bhelgaas: commit log]

## References
- https://git.kernel.org/stable/c/0e6d92e3b973de78eb7015154cf1197af9fac5c9
- https://git.kernel.org/stable/c/242ee2b0ad9b23f47084904fce3f9f228068a1f9
- https://git.kernel.org/stable/c/5089b3d874e9933d9842e90410d3af1520494757
- https://git.kernel.org/stable/c/c8b9d6b7d62a444e0bca5b9ae28f9f2b0f52feef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56689.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56689
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

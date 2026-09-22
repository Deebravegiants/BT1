# [M] PCI: of_property: Return error for int_map allocation failure

## Summary
Severity: Medium
Advisory: CVE-2024-34030
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-34030
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: of_property: Return error for int_map allocation failure

Return -ENOMEM from of_pci_prop_intr_map() if kcalloc() fails to prevent a
NULL pointer dereference in this case.

[bhelgaas: commit log]

## References
- https://git.kernel.org/stable/c/598e4a37a2f8da9144ba1fab04320c32169b6d0d
- https://git.kernel.org/stable/c/b5f31d1470c4fdfae368feeb389768ba8d24fb34
- https://git.kernel.org/stable/c/e6f7d27df5d208b50cae817a91d128fb434bb12c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34030.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

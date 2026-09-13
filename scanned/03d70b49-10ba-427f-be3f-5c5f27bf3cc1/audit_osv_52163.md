# [M] CVE-2021-47147

## Summary
Severity: Medium
Advisory: CVE-2021-47147
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47147
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: ocp: Fix a resource leak in an error handling path

If an error occurs after a successful 'pci_ioremap_bar()' call, it must be
undone by a corresponding 'pci_iounmap()' call, as already done in the
remove function.

## References
- https://git.kernel.org/stable/c/0e38e702f1152479e6afac34f151dbfd99417f99
- https://git.kernel.org/stable/c/9c1bb37f8cad5e2ee1933fa1da9a6baa7876a8e4

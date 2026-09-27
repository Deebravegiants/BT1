# [C] PCI: dwc: ep: Prevent changing BAR size/flags in pci_epc_set_bar()

## Summary
Severity: Critical
Advisory: CVE-2024-58006
Ecosystem: Linux
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58006
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: dwc: ep: Prevent changing BAR size/flags in pci_epc_set_bar()

In commit 4284c88fff0e ("PCI: designware-ep: Allow pci_epc_set_bar() update
inbound map address") set_bar() was modified to support dynamically
changing the backing physical address of a BAR that was already configured.

This means that set_bar() can be called twice, without ever calling
clear_bar() (as calling clear_bar() would clear the BAR's PCI address
assigned by the host).

This can only be done if the new BAR size/flags does not differ from the
existing BAR configuration. Add these missing checks.

If we allow set_bar() to set e.g. a new BAR size that differs from the
existing BAR size, the new address translation range will be smaller than
the BAR size already determined by the host, which would mean that a read
past the new BAR size would pass the iATU untranslated, which could allow
the host to read memory not belonging to the new struct pci_epf_bar.

While at it, add comments which clarifies the support for dynamically
changing the physical address of a BAR. (Which was also missing.)

## References
- https://git.kernel.org/stable/c/3229c15d6267de8e704b4085df8a82a5af2d63eb
- https://git.kernel.org/stable/c/3708acbd5f169ebafe1faa519cb28adc56295546
- https://git.kernel.org/stable/c/b5cacfd067060c75088363ed3e19779078be2755
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58006.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

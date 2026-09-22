# [H] PCI/ASPM: Disable ASPM on MFD function removal to avoid use-after-free

## Summary
Severity: High
Advisory: CVE-2023-53446
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53446
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI/ASPM: Disable ASPM on MFD function removal to avoid use-after-free

Struct pcie_link_state->downstream is a pointer to the pci_dev of function
0.  Previously we retained that pointer when removing function 0, and
subsequent ASPM policy changes dereferenced it, resulting in a
use-after-free warning from KASAN, e.g.:

  # echo 1 > /sys/bus/pci/devices/0000:03:00.0/remove
  # echo powersave > /sys/module/pcie_aspm/parameters/policy

  BUG: KASAN: slab-use-after-free in pcie_config_aspm_link+0x42d/0x500
  Call Trace:
   kasan_report+0xae/0xe0
   pcie_config_aspm_link+0x42d/0x500
   pcie_aspm_set_policy+0x8e/0x1a0
   param_attr_store+0x162/0x2c0
   module_attr_store+0x3e/0x80

PCIe spec r6.0, sec 7.5.3.7, recommends that software program the same ASPM
Control value in all functions of multi-function devices.

Disable ASPM and free the pcie_link_state when any child function is
removed so we can discard the dangling pcie_link_state->downstream pointer
and maintain the same ASPM Control configuration for all functions.

[bhelgaas: commit log and comment]

## References
- https://git.kernel.org/stable/c/4203722d51afe3d239e03f15cc73efdf023a7103
- https://git.kernel.org/stable/c/456d8aa37d0f56fc9e985e812496e861dcd6f2f2
- https://git.kernel.org/stable/c/666e7f9d60cee23077ea3e6331f6f8a19f7ea03f
- https://git.kernel.org/stable/c/7aecdd47910c51707696e8b0e045b9f88bd4230f
- https://git.kernel.org/stable/c/7badf4d6f49a358a01ab072bbff88d3ee886c33b
- https://git.kernel.org/stable/c/9856c0de49052174ab474113f4ba40c02aaee086
- https://git.kernel.org/stable/c/d51d2eeae4ce54d542909c4d9d07bf371a78592c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53446.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

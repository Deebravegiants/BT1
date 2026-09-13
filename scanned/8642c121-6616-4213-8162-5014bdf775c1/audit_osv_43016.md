# [C] net/liquidio: drop cached VF pci_dev LUT

## Summary
Severity: Critical
Advisory: CVE-2026-72329
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72329
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/liquidio: drop cached VF pci_dev LUT

The PF SR-IOV enable path caches VF pci_dev pointers in
dpiring_to_vfpcidev_lut[] by iterating with pci_get_device(). Those
entries do not own a reference, because the iterator drops the previous
device reference on each step. The cached pointer is then dereferenced
later when handling OCTEON_VF_FLR_REQUEST.

Replace the cached VF mapping with runtime lookup on the mailbox DPI
ring: derive the VF index from q_no, resolve the VF via exported PCI
IOV helpers, validate it with the PF pointer and VF ID, then issue
pcie_flr() and drop the reference with pci_dev_put(). Remove the
unused VF lookup table initialization and cleanup.

## References
- https://git.kernel.org/stable/c/5c0e3ba4f500fd4314ceb42f07f16bc445156431
- https://git.kernel.org/stable/c/81acef3a247fd523513a2e9f71de1c167bc0f882
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72329.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

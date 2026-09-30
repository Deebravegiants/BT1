# [H] PCI/IOV: Skip VF Resizable BAR restore on read error

## Summary
Severity: High
Advisory: CVE-2026-64460
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64460
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI/IOV: Skip VF Resizable BAR restore on read error

sriov_restore_vf_rebar_state() uses the VF Resizable BAR Control register
to decide how many VF BARs to restore (nbars) and which VF BAR each
iteration addresses (bar_idx). bar_idx indexes into dev->sriov->barsz[],
which has only PCI_SRIOV_NUM_BARS (6) entries.

When a device does not respond, config reads typically return
PCI_ERROR_RESPONSE (~0).  Both fields are 3 bits wide, so nbars and bar_idx
both evaluate to 7. The barsz[] access then goes out of bounds.  UBSAN
reports this as:

  UBSAN: array-index-out-of-bounds in drivers/pci/iov.c:948:51 index 7 is out of range for type 'resource_size_t [6]'

Observed on an NVIDIA RTX PRO 1000 GPU (GB207GLM) that stopped responding
during a failed GC6 power state exit. The subsequent pci_restore_state()
invoked sriov_restore_vf_rebar_state() while config reads returned
0xffffffff, triggering the splat.

Bail out if any VF Resizable BAR Control read returns PCI_ERROR_RESPONSE.
No further VF BARs are touched, which is safe because a config read that
returns PCI_ERROR_RESPONSE indicates the device is unreachable and
restoration is pointless. This mirrors the guard in
pci_restore_rebar_state().

## References
- https://git.kernel.org/stable/c/55fd485e66d0ad5c762c23dba1461fe9c741cd96
- https://git.kernel.org/stable/c/b77524621250407386f44c6eea7e5e4619ada1ce
- https://git.kernel.org/stable/c/f34f1712229d71ce4286440fef12526fd4590b37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64460.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64460
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

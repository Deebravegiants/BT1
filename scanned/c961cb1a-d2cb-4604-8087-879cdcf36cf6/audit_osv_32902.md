# [H] cxl/ras: Fix CPER handler device confusion

## Summary
Severity: High
Advisory: CVE-2025-38252
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38252
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/ras: Fix CPER handler device confusion

By inspection, cxl_cper_handle_prot_err() is making a series of fragile
assumptions that can lead to crashes:

1/ It assumes that endpoints identified in the record are a CXL-type-3
   device, nothing guarantees that.

2/ It assumes that the device is bound to the cxl_pci driver, nothing
   guarantees that.

3/ Minor, it holds the device lock over the switch-port tracing for no
   reason as the trace is 100% generated from data in the record.

Correct those by checking that the PCIe endpoint parents a cxl_memdev
before assuming the format of the driver data, and move the lock to where
it is required. Consequently this also makes the implementation ready for
CXL accelerators that are not bound to cxl_pci.

## References
- https://git.kernel.org/stable/c/3c70ec71abdaf4e4fa48cd8fdfbbd864d78235a8
- https://git.kernel.org/stable/c/4bcb8dd36e9e3fad6c22862ac5b6993df838309b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38252.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38252
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

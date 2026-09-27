# [H] misc: pci_endpoint_test: Free IRQs before removing the device

## Summary
Severity: High
Advisory: CVE-2023-54326
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54326
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: pci_endpoint_test: Free IRQs before removing the device

In pci_endpoint_test_remove(), freeing the IRQs after removing the device
creates a small race window for IRQs to be received with the test device
memory already released, causing the IRQ handler to access invalid memory,
resulting in an oops.

Free the device IRQs before removing the device to avoid this issue.

## References
- https://git.kernel.org/stable/c/14bdee38e96c7d37ca15e7bea50411eee25fe315
- https://git.kernel.org/stable/c/38d12bcf4e2ce3d285eb29644a79a54f42040fab
- https://git.kernel.org/stable/c/c2dba13bc0c62b79a3cbe4bfe5faa32231bf9b55
- https://git.kernel.org/stable/c/cdf9a7e2cdc7a5464e3cc6d0b715ba2b1d215521
- https://git.kernel.org/stable/c/dd2210379205fcd23a9d8869b0cef90e3770577c
- https://git.kernel.org/stable/c/f61b7634a3249d12b9daa36ffbdb9965b6f24c6c
- https://git.kernel.org/stable/c/fb7f8bdb886f2ebf35ee5edaf2bf5f02b063ddb7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54326.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54326
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] misc: pci_endpoint_test: Fix array underflow in pci_endpoint_test_ioctl()

## Summary
Severity: High
Advisory: CVE-2025-40117
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: pci_endpoint_test: Fix array underflow in pci_endpoint_test_ioctl()

Commit eefb83790a0d ("misc: pci_endpoint_test: Add doorbell test case")
added NO_BAR (-1) to the pci_barno enum which, in practical terms,
changes the enum from an unsigned int to a signed int.  If the user
passes a negative number in pci_endpoint_test_ioctl() then it results in
an array underflow in pci_endpoint_test_bar().

## References
- https://git.kernel.org/stable/c/1ad82f9db13d85667366044acdfb02009d576c5a
- https://git.kernel.org/stable/c/6df3687922570f753574c40b35e83b26b32292d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40117.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

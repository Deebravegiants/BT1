# [C] net: ena: Add validation for completion descriptors consistency

## Summary
Severity: Critical
Advisory: CVE-2024-40999
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40999
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ena: Add validation for completion descriptors consistency

Validate that `first` flag is set only for the first
descriptor in multi-buffer packets.
In case of an invalid descriptor, a reset will occur.
A new reset reason for RX data corruption has been added.

## References
- https://git.kernel.org/stable/c/42146ee5286f16f1674a84f7c274dcca65c6ff2e
- https://git.kernel.org/stable/c/b37b98a3a0c1198bafe8c2d9ce0bc845b4e7a9a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40999.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

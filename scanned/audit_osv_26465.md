# [H] thermal/drivers/hisi: Drop second sensor hi3660

## Summary
Severity: High
Advisory: CVE-2023-53242
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53242
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal/drivers/hisi: Drop second sensor hi3660

The commit 74c8e6bffbe1 ("driver core: Add __alloc_size hint to devm
allocators") exposes a panic "BRK handler: Fatal exception" on the
hi3660_thermal_probe funciton.
This is because the function allocates memory for only one
sensors array entry, but tries to fill up a second one.

Fix this by removing the unneeded second access.

## References
- https://git.kernel.org/stable/c/15cc25829a97c3957e520e971868aacc84341317
- https://git.kernel.org/stable/c/3cf2181e438f43ed24e12424fe36d156cca233b9
- https://git.kernel.org/stable/c/68e675a9b69cfc34dd915d91a4650e3ee53421f4
- https://git.kernel.org/stable/c/9f6756cd09889c7201ee31e6f76fbd914fb0b80d
- https://git.kernel.org/stable/c/e02bc492883abf751fd1a8d89fc025fbce6744c6
- https://git.kernel.org/stable/c/f5aaf140ab1c02889c088e1b1098adad600541af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53242.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

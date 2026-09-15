# [M] arm64: acpi: Fix possible memory leak of ffh_ctxt

## Summary
Severity: Medium
Advisory: CVE-2023-53266
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53266
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: acpi: Fix possible memory leak of ffh_ctxt

Allocated 'ffh_ctxt' memory leak is possible if the SMCCC version
and conduit checks fail and -EOPNOTSUPP is returned without freeing the
allocated memory.

Fix the same by moving the allocation after the SMCCC version and
conduit checks.

## References
- https://git.kernel.org/stable/c/1b561d3949f8478c5403c9752b5533211a757226
- https://git.kernel.org/stable/c/7521da2eb42d65f89f511b7912d3757cf3d9168a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53266.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

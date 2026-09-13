# [M] ice: Block switchdev mode when ADQ is active and vice versa

## Summary
Severity: Medium
Advisory: CVE-2023-53442
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53442
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: Block switchdev mode when ADQ is active and vice versa

ADQ and switchdev are not supported simultaneously. Enabling both at the
same time can result in nullptr dereference.

To prevent this, check if ADQ is active when changing devlink mode to
switchdev mode, and check if switchdev is active when enabling ADQ.

## References
- https://git.kernel.org/stable/c/1c82d1b736ce85e77fd4da05eca6f1f4a52a2bc3
- https://git.kernel.org/stable/c/24f0d69da35d812b3a1104918014a29627140cb1
- https://git.kernel.org/stable/c/43d00e102d9ecbe2635d7e3f2e14d2e90183d6af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53442.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

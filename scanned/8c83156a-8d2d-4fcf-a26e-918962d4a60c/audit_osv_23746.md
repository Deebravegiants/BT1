# [M] powerpc/xive: Fix refcount leak in xive_spapr_init

## Summary
Severity: Medium
Advisory: CVE-2022-49437
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49437
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/xive: Fix refcount leak in xive_spapr_init

of_find_compatible_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/1d1fb9618bdd5a5fbf9a9eb75133da301d33721c
- https://git.kernel.org/stable/c/65f11ccdd746e0e7f0b469cc989ba43d4f30ecfe
- https://git.kernel.org/stable/c/6e806485d851986a2445267608f27cb4ba2ed774
- https://git.kernel.org/stable/c/cc62dde2a5f4ba14016fd9caec76f08d388f4b9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49437.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

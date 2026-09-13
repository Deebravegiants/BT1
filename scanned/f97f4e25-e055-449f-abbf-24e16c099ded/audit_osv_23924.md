# [M] ARM: Fix refcount leak in axxia_boot_secondary

## Summary
Severity: Medium
Advisory: CVE-2022-49679
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49679
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: Fix refcount leak in axxia_boot_secondary

of_find_compatible_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/29ca9c4efacccdc15104a8d4bf10b5183fc92840
- https://git.kernel.org/stable/c/3c19fe3f04f4f4e7a2b722c2fd3c98356fc1d72b
- https://git.kernel.org/stable/c/44a5b3a073e5aaa5720929dba95b2725eb32bb65
- https://git.kernel.org/stable/c/4d9c60e868f7cf8e09956e7d5bb44d807d712699
- https://git.kernel.org/stable/c/71e12e5b02674459a24f16e965255d63b31fe049
- https://git.kernel.org/stable/c/7c7ff68daa93d8c4cdea482da4f2429c0398fcde
- https://git.kernel.org/stable/c/a9b76c232a1ce4cbf27862097f7eb634dcc779eb
- https://git.kernel.org/stable/c/b385cb59aac8d61c29bc72ebf3d19a536914af96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49679.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

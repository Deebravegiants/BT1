# [M] ARM: meson: Fix refcount leak in meson_smp_prepare_cpus

## Summary
Severity: Medium
Advisory: CVE-2022-49656
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49656
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.252, >=4.20.0 <5.4.205, >=5.5.0 <5.10.130, >=5.11.0 <5.15.54, >=5.16.0 <5.18.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: meson: Fix refcount leak in meson_smp_prepare_cpus

of_find_compatible_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/2e1bcd33478ef44e63a45457055060b5fe4118ad
- https://git.kernel.org/stable/c/34d2cd3fccced12b958b8848e3eff0ee4296764c
- https://git.kernel.org/stable/c/3cf8ece9113242c10f83c7675ea4f4f67959ee43
- https://git.kernel.org/stable/c/3d90607e7e6afa89768b0aaa915b58bd2b849276
- https://git.kernel.org/stable/c/7208101ded1e9dcc52c8f0f8b16474211c871c1a
- https://git.kernel.org/stable/c/c5fbf4f74c94fd60d5e9bf9f7f8268c3601562ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49656.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

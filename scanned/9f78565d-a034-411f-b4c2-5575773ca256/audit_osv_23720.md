# [M] net: ethernet: ti: am65-cpsw-nuss: Fix some refcount leaks

## Summary
Severity: Medium
Advisory: CVE-2022-49386
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49386
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw-nuss: Fix some refcount leaks

of_get_child_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
am65_cpsw_init_cpts() and am65_cpsw_nuss_probe() don't release
the refcount in error case.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/2e44f21c384503562713b7d3b673c40bed20af3d
- https://git.kernel.org/stable/c/5dd89d2fc438457811cbbec07999ce0d80051ff5
- https://git.kernel.org/stable/c/78aca10a16f001c9f49f1cc4dadfee8d444bb173
- https://git.kernel.org/stable/c/a4b7ef3b159805ba6be061d0cd2403d84b9b0063
- https://git.kernel.org/stable/c/f7ba2cc57f404d2d9f26fb85bd3833d35a477829
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49386.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

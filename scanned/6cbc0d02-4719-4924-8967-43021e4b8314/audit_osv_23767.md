# [M] thermal/drivers/imx_sc_thermal: Fix refcount leak in imx_sc_thermal_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49463
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49463
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal/drivers/imx_sc_thermal: Fix refcount leak in imx_sc_thermal_probe

of_find_node_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/09700c504d8e63faffd2a2235074e8c5d130cb8f
- https://git.kernel.org/stable/c/0ec10303c10833c1bcba7a1bde2f297e494d5464
- https://git.kernel.org/stable/c/3ade442ea5d3512a3c67984489ab4d8a6fb3b29f
- https://git.kernel.org/stable/c/8bbf522a2c51ef939d0e8835e236bfcd252193af
- https://git.kernel.org/stable/c/ec0925b731697db7cab5944a3e55d2d58bb3d075
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49463.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49463
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

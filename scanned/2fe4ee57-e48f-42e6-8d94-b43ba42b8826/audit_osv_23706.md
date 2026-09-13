# [M] net: dsa: mv88e6xxx: Fix refcount leak in mv88e6xxx_mdios_register

## Summary
Severity: Medium
Advisory: CVE-2022-49367
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49367
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: mv88e6xxx: Fix refcount leak in mv88e6xxx_mdios_register

of_get_child_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.

mv88e6xxx_mdio_register() pass the device node to of_mdiobus_register().
We don't need the device node after it.

Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/02ded5a173619b11728b8bf75a3fd995a2c1ff28
- https://git.kernel.org/stable/c/42658e47f1abbbe592007d3ba303de466114d0bb
- https://git.kernel.org/stable/c/86c3c5f8e4bd1325e24f6fba9017cade29933377
- https://git.kernel.org/stable/c/8a1a1255152da4fb934290e7ababc66f24985520
- https://git.kernel.org/stable/c/a101793994c0a14c70bb4e44c7fda597eeebba0a
- https://git.kernel.org/stable/c/c1df9cb756e5a9ba1841648c44ee5d92306b9c65
- https://git.kernel.org/stable/c/dc1cf8c6f9793546696fded437a5b4c84944c48b
- https://git.kernel.org/stable/c/e0d763d0c7665c7897e4f5a0847ab0c82543345f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49367.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

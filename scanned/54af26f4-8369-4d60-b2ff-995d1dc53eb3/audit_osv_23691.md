# [M] net: ethernet: bgmac: Fix refcount leak in bcma_mdio_mii_register

## Summary
Severity: Medium
Advisory: CVE-2022-49342
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49342
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: bgmac: Fix refcount leak in bcma_mdio_mii_register

of_get_child_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/7fb1fe7d9a167205413f1de8db9f7d0f82c78286
- https://git.kernel.org/stable/c/b51996e35bbfcc7a27d94dfeed5cc2429b2c0df4
- https://git.kernel.org/stable/c/b8d91399775c55162073bb2aca061ec42e3d4bc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49342.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49342
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

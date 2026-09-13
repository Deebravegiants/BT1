# [M] PCI: mediatek: Fix refcount leak in mtk_pcie_subsys_powerup()

## Summary
Severity: Medium
Advisory: CVE-2022-49454
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49454
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: mediatek: Fix refcount leak in mtk_pcie_subsys_powerup()

The of_find_compatible_node() function returns a node pointer with
refcount incremented, We should use of_node_put() on it when done
Add the missing of_node_put() to release the refcount.

## References
- https://git.kernel.org/stable/c/09b2d906d78ddf5042b1f3e0091835fc6997e8a4
- https://git.kernel.org/stable/c/214e0d8fe4a813ae6ffd62bc2dfe7544c20914f4
- https://git.kernel.org/stable/c/4cef4237d6c37257cb6ddc397723e9c0dded0efe
- https://git.kernel.org/stable/c/ad1c9d13e04509ae24fae8dd2897148657323519
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49454.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

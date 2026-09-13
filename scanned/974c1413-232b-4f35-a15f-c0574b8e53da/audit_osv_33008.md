# [H] net: airoha: fix potential use-after-free in airoha_npu_get()

## Summary
Severity: High
Advisory: CVE-2025-38536
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38536
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: airoha: fix potential use-after-free in airoha_npu_get()

np->name was being used after calling of_node_put(np), which
releases the node and can lead to a use-after-free bug.
Previously, of_node_put(np) was called unconditionally after
of_find_device_by_node(np), which could result in a use-after-free if
pdev is NULL.

This patch moves of_node_put(np) after the error check to ensure
the node is only released after both the error and success cases
are handled appropriately, preventing potential resource issues.

## References
- https://git.kernel.org/stable/c/3cd582e7d0787506990ef0180405eb6224fa90a6
- https://git.kernel.org/stable/c/df6bf96b41e547e350667bc4c143be53646d070d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38536.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

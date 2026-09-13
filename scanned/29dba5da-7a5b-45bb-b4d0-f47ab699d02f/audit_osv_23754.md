# [M] ARM: hisi: Add missing of_node_put after of_find_compatible_node

## Summary
Severity: Medium
Advisory: CVE-2022-49447
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49447
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: hisi: Add missing of_node_put after of_find_compatible_node

of_find_compatible_node  will increment the refcount of the returned
device_node. Calling of_node_put() to avoid the refcount leak

## References
- https://git.kernel.org/stable/c/21a3effe446dd6dc5eed7fe897c2f9b88c9a5d6d
- https://git.kernel.org/stable/c/45d211668d33c49d73f5213e8c2b58468108647c
- https://git.kernel.org/stable/c/46cb7868811d025c3d29c10d18b3422db1cf20d5
- https://git.kernel.org/stable/c/9bc72e47d4630d58a840a66a869c56b29554cfe4
- https://git.kernel.org/stable/c/a3265a9440030068547a20dfee646666f3ca5278
- https://git.kernel.org/stable/c/cafaaae4bb9ce84a2791fa29bf6907a9466c3883
- https://git.kernel.org/stable/c/dd4be8ecfb41a29e7c4e551b4e866157ce4a3429
- https://git.kernel.org/stable/c/e109058165137ef42841abd989f080adfefa14fa
- https://git.kernel.org/stable/c/f8da78b2bae1f54746647a2bb44f8bd6025c57af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49447.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

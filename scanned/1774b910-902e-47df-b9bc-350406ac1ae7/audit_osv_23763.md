# [M] ARM: versatile: Add missing of_node_put in dcscb_init

## Summary
Severity: Medium
Advisory: CVE-2022-49457
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49457
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: versatile: Add missing of_node_put in dcscb_init

The device_node pointer is returned by of_find_compatible_node
with refcount incremented. We should use of_node_put() to avoid
the refcount leak.

## References
- https://git.kernel.org/stable/c/23b44f9c649bbef10b45fa33080cd8b4166800ae
- https://git.kernel.org/stable/c/2d7b23db35254b7d46e852967090c64cdccf24da
- https://git.kernel.org/stable/c/3c6006faed9aba5144b33176d061031a9be66954
- https://git.kernel.org/stable/c/83c329b980bddbc8c6a3d287d91f2103a4d4a860
- https://git.kernel.org/stable/c/a0fc05cd17617e63fc13ad0c01f3f0afd890d8ec
- https://git.kernel.org/stable/c/bbdfb7d4f036118d36415a2575efa6f5246505ae
- https://git.kernel.org/stable/c/d146e2a9864ade19914494de3fb520390b415d58
- https://git.kernel.org/stable/c/d6de7b181c29cd4578ec139aafb5eac062abbe1b
- https://git.kernel.org/stable/c/fcd1999ba97445a12cc394f5f42ffd9116bf0185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49457.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49457
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

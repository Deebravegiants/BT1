# [M] dmaengine: ti: Fix refcount leak in ti_dra7_xbar_route_allocate

## Summary
Severity: Medium
Advisory: CVE-2022-49652
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49652
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <4.9.323, >=4.10.0 <4.14.288, >=4.15.0 <4.19.252, >=4.20.0 <5.4.205, >=5.5.0 <5.10.130, >=5.11.0 <5.15.54, >=5.16.0 <5.18.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: ti: Fix refcount leak in ti_dra7_xbar_route_allocate

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not needed anymore.

Add missing of_node_put() in to fix this.

## References
- https://git.kernel.org/stable/c/37147e22cd8dfc0412495cb361708836157a4486
- https://git.kernel.org/stable/c/3bd66010398871807c1cebacee07d60ded1b1402
- https://git.kernel.org/stable/c/452b9dfd7aca96befce22634fadb111737f22bbe
- https://git.kernel.org/stable/c/61b4ef19c346dc21ab1d4f39f5c412e3037b2bdc
- https://git.kernel.org/stable/c/b31ab132561c7f1b6459039152b8d09e44eb3565
- https://git.kernel.org/stable/c/b5a817f8d62e9e13280928f3756e54854ae4962e
- https://git.kernel.org/stable/c/c132fe78ad7b4ce8b5d49a501a15c29d08eeb23a
- https://git.kernel.org/stable/c/cb9813d7eae917acd34436160a278b8b5d48ca53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49652.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49652
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

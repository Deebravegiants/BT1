# [M] ARM: exynos: Fix refcount leak in exynos_map_pmu

## Summary
Severity: Medium
Advisory: CVE-2022-49680
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49680
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: exynos: Fix refcount leak in exynos_map_pmu

of_find_matching_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.
of_node_put() checks null pointer.

## References
- https://git.kernel.org/stable/c/31d09571bb071c20f6bdc0bb7ac1ef8dd2987c04
- https://git.kernel.org/stable/c/545ae5cbae839ce39bfe09828e413f1c916082de
- https://git.kernel.org/stable/c/68f28d52e6cbab8dcfa249cac4356d1d0573e868
- https://git.kernel.org/stable/c/7571bcecf01b69f0d3ec60ca41ce5d4c75411a4a
- https://git.kernel.org/stable/c/c4c79525042a4a7df96b73477feaf232fe44ae81
- https://git.kernel.org/stable/c/d23f76018e17618559da9eea179d137362023f95
- https://git.kernel.org/stable/c/f9b77a52937582a5b99a5a07e4ef1e2f48f87347
- https://git.kernel.org/stable/c/fc354856e9fad9cd36e2ad28f9da70716025055a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49680.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

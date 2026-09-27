# [M] irqchip/gic/realview: Fix refcount leak in realview_gic_of_init

## Summary
Severity: Medium
Advisory: CVE-2022-49719
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49719
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic/realview: Fix refcount leak in realview_gic_of_init

of_find_matching_node_and_match() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/16b603cb8d34c2d917983918db1f88c8b831baaa
- https://git.kernel.org/stable/c/486f68f85085d9b16ae097679b1486dcb1b6eb69
- https://git.kernel.org/stable/c/56526c3883fc7a1f5898b1d40a02c8b8685a5d92
- https://git.kernel.org/stable/c/5d38720661a4b9c87705c206a6081177ffb8ec1d
- https://git.kernel.org/stable/c/87da903ce632d5689bef66d56ee5dae700d82104
- https://git.kernel.org/stable/c/b634af84bc1edece4e63317b0ad95618dd3a8693
- https://git.kernel.org/stable/c/e52a58b79f11755ea7e877015c4a1704303fa55f
- https://git.kernel.org/stable/c/f4b98e314888cc51486421bcf6d52852452ea48b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49719.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49719
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

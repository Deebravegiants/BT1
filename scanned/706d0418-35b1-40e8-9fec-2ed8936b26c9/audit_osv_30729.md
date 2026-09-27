# [H] net: renesas: rswitch: avoid use-after-put for a device tree node

## Summary
Severity: High
Advisory: CVE-2024-55639
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-55639
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: renesas: rswitch: avoid use-after-put for a device tree node

The device tree node saved in the rswitch_device structure is used at
several driver locations. So passing this node to of_node_put() after
the first use is wrong.

Move of_node_put() for this node to exit paths.

## References
- https://git.kernel.org/stable/c/66b7e9f85b8459c823b11e9af69dbf4be5eb6be8
- https://git.kernel.org/stable/c/92007a28f95413058a7268dc84e5f44b700165d1
- https://git.kernel.org/stable/c/bf8c6755f02029d1eddc3ff19b870240f054afc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55639.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55639
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] irqchip/realtek-rtl: Fix refcount leak in map_interrupts

## Summary
Severity: Medium
Advisory: CVE-2022-49714
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49714
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/realtek-rtl: Fix refcount leak in map_interrupts

of_find_node_by_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
This function doesn't call of_node_put() in error path.
Call of_node_put() directly after of_property_read_u32() to cover
both normal path and error path.

## References
- https://git.kernel.org/stable/c/e85b1b797de0e7a271b906291ce28245822820b8
- https://git.kernel.org/stable/c/eff4780f83d0ae3e5b6c02ff5d999dc4c1c5c8ce
- https://git.kernel.org/stable/c/f6d6223df0666fbc054e3a8c6ac14eb0af37c286
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49714.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49714
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

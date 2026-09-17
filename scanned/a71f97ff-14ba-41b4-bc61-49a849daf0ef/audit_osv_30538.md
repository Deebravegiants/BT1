# [H] vdpa: solidrun: Fix UB bug with devres

## Summary
Severity: High
Advisory: CVE-2024-53126
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53126
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vdpa: solidrun: Fix UB bug with devres

In psnet_open_pf_bar() and snet_open_vf_bar() a string later passed to
pcim_iomap_regions() is placed on the stack. Neither
pcim_iomap_regions() nor the functions it calls copy that string.

Should the string later ever be used, this, consequently, causes
undefined behavior since the stack frame will by then have disappeared.

Fix the bug by allocating the strings on the heap through
devm_kasprintf().

## References
- https://git.kernel.org/stable/c/0b364cf53b20204e92bac7c6ebd1ee7d3ec62931
- https://git.kernel.org/stable/c/5bb287da2d2d5bb8f7376e223b02edb16998982e
- https://git.kernel.org/stable/c/d372dd09cfbf1324f54cbffd81fcaf6cdf3e608e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53126.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53126
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

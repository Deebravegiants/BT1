# [H] pinctrl: nuvoton: fix a double free in ma35_pinctrl_dt_node_to_map_func()

## Summary
Severity: High
Advisory: CVE-2024-50071
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50071
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: nuvoton: fix a double free in ma35_pinctrl_dt_node_to_map_func()

'new_map' is allocated using devm_* which takes care of freeing the
allocated data on device removal, call to

	.dt_free_map = pinconf_generic_dt_free_map

double frees the map as pinconf_generic_dt_free_map() calls
pinctrl_utils_free_map().

Fix this by using kcalloc() instead of auto-managed devm_kcalloc().

## References
- https://git.kernel.org/stable/c/3fd976afe9743110f20a23f93b7ff9693f2be4bf
- https://git.kernel.org/stable/c/6441d9c3d71b59c8fd27d4e381c7471a32ac1a68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50071.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

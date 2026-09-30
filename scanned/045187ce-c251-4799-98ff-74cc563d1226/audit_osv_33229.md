# [H] ixgbe: fix incorrect map used in eee linkmode

## Summary
Severity: High
Advisory: CVE-2025-39922
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39922
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ixgbe: fix incorrect map used in eee linkmode

incorrectly used ixgbe_lp_map in loops intended to populate the
supported and advertised EEE linkmode bitmaps based on ixgbe_ls_map.
This results in incorrect bit setting and potential out-of-bounds
access, since ixgbe_lp_map and ixgbe_ls_map have different sizes
and purposes.

ixgbe_lp_map[i] -> ixgbe_ls_map[i]

Use ixgbe_ls_map for supported and advertised linkmodes, and keep
ixgbe_lp_map usage only for link partner (lp_advertised) mapping.

## References
- https://git.kernel.org/stable/c/129c1cb8a081a02d99267cb51708f1326395f4e8
- https://git.kernel.org/stable/c/682105ab63826fb7ca7c112b42b478d156fbb19f
- https://git.kernel.org/stable/c/b7e5c3e3bfa9dc8af75ff6d8633ad7070e1985e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39922.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

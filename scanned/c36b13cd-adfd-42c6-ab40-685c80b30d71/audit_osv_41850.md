# [H] ethtool: coalesce: cap profile updates at NET_DIM_PARAMS_NUM_PROFILES

## Summary
Severity: High
Advisory: CVE-2026-63987
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63987
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: coalesce: cap profile updates at NET_DIM_PARAMS_NUM_PROFILES

ethnl_update_profile() walks the ETHTOOL_A_PROFILE_IRQ_MODERATION
nest list with an index 'i' and writes new_profile[i++] without
bounding i. The destination is kmemdup()'d at NET_DIM_PARAMS_NUM_PROFILES
entries (5), but the Netlink nest count is entirely user-controlled.
Netlink policies do not have support for constraining the number
of nested entries (or number of multi-attr entries).

## References
- https://git.kernel.org/stable/c/0c02c190bcd9822477038ff2cee10ea584ac1b1d
- https://git.kernel.org/stable/c/6205f7166d2dd14a017a5802c81e5bd1421a8635
- https://git.kernel.org/stable/c/7281b096b072f6c6e30420e3467d738f2e4c4b57
- https://git.kernel.org/stable/c/d4c9cc7c47781c6f4fa29d80a1193a8bcd1525bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63987.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63987
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] ice: fix FDIR CTRL VSI resource leak in ice_reset_all_vfs()

## Summary
Severity: High
Advisory: CVE-2026-72425
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72425
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix FDIR CTRL VSI resource leak in ice_reset_all_vfs()

Resetting all VFs causes resource leak on VFs with FDIR filters
enabled as CTRL VSIs are only invalidated and not freed. Fix by using
ice_vf_ctrl_vsi_release() instead of ice_vf_ctrl_invalidate_vsi() which
aligns behavior with the ice_reset_vf() function.

Reproduction:
  echo 1 > /sys/class/net/$pf/device/sriov_numvfs
  ethtool -N $vf flow-type ether proto 0x9000 action 0
  echo 1 > /sys/class/net/$pf/device/reset

## References
- https://git.kernel.org/stable/c/335c2dd21ad9d520102906f96edb99fd5e89ac32
- https://git.kernel.org/stable/c/87a042e45bf4870dc75ea05b4fc0286abecb2a4d
- https://git.kernel.org/stable/c/b1fc5bafbc5f84df457b6f987ac993e0802f8d93
- https://git.kernel.org/stable/c/b409a9dc37db8bd798122fc5bcdcfaccaf80db1e
- https://git.kernel.org/stable/c/dd6d8e4412f805937f61f00bbfdfe831978be235
- https://git.kernel.org/stable/c/ebbe8868cf473f698e0fbaf436d2618b2bcda806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

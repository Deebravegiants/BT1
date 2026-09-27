# [H] net: dsa: Avoid cross-chip syncing of VLAN filtering

## Summary
Severity: High
Advisory: CVE-2022-49234
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49234
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: Avoid cross-chip syncing of VLAN filtering

Changes to VLAN filtering are not applicable to cross-chip
notifications.

On a system like this:

.-----.   .-----.   .-----.
| sw1 +---+ sw2 +---+ sw3 |
'-1-2-'   '-1-2-'   '-1-2-'

Before this change, upon sw1p1 leaving a bridge, a call to
dsa_port_vlan_filtering would also be made to sw2p1 and sw3p1.

In this scenario:

.---------.   .-----.   .-----.
|   sw1   +---+ sw2 +---+ sw3 |
'-1-2-3-4-'   '-1-2-'   '-1-2-'

When sw1p4 would leave a bridge, dsa_port_vlan_filtering would be
called for sw2 and sw3 with a non-existing port - leading to array
out-of-bounds accesses and crashes on mv88e6xxx.

## References
- https://git.kernel.org/stable/c/108dc8741c203e9d6ce4e973367f1bac20c7192b
- https://git.kernel.org/stable/c/e1f2a4dd8d433eec393d09273a78a3d3551339cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49234.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

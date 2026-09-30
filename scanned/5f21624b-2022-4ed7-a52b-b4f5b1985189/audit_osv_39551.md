# [H] wifi: mac80211: remove station if connection prep fails

## Summary
Severity: High
Advisory: CVE-2026-46125
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46125
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: remove station if connection prep fails

If connection preparation fails for MLO connections, then the
interface is completely reset to non-MLD. In this case, we must
not keep the station since it's related to the link of the vif
being removed. Delete an existing station. Any "new_sta" is
already being removed, so that doesn't need changes.

This fixes a use-after-free/double-free in debugfs if that's
enabled, because a vif going from MLD (and to MLD, but that's
not relevant here) recreates its entire debugfs.

## References
- https://git.kernel.org/stable/c/18fed0a209500bfea5c4c08609ec93855e4e500b
- https://git.kernel.org/stable/c/1c2b72ea89882aeb948340498391e69c58d466f1
- https://git.kernel.org/stable/c/283fc9e44ff5b5ac967439b4951b80bd4299f4e4
- https://git.kernel.org/stable/c/9e28654f79f443bca9b29ff3ae7cf18abfba58a0
- https://git.kernel.org/stable/c/afcbaed89cdc1a001b43270cbf5394bb4804270a
- https://git.kernel.org/stable/c/fe75fa1ac9a92990f7fc3d34b17808fd933071b2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46125.json
- https://access.redhat.com/errata/RHSA-2026:26427
- https://access.redhat.com/errata/RHSA-2026:26428
- https://access.redhat.com/errata/RHSA-2026:26462
- https://access.redhat.com/errata/RHSA-2026:26515
- https://access.redhat.com/errata/RHSA-2026:26563
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:27708
- https://access.redhat.com/errata/RHSA-2026:27731
- https://access.redhat.com/errata/RHSA-2026:27735
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/security/cve/CVE-2026-46125
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46125.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46125

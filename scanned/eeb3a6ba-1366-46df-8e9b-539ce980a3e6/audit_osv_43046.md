# [H] afs: Fix missing NULL pointer check in afs_break_some_callbacks()

## Summary
Severity: High
Advisory: CVE-2026-72373
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72373
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix missing NULL pointer check in afs_break_some_callbacks()

Fix afs_break_some_callbacks() to check to see if afs_lookup_volume_rcu()
returned NULL (e.g. the specified volume is unknown).

## References
- https://git.kernel.org/stable/c/5492799ec5d27be3bd454dcaf046bc7054f637ae
- https://git.kernel.org/stable/c/794a01110390c1b76f59ece773fb0fbfd89c6f5c
- https://git.kernel.org/stable/c/a99a617701186dc68c7b330d35fc2253f48e2ab2
- https://git.kernel.org/stable/c/e3e59ff22a0de01ed0cf3a3e25558811abc3b70a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

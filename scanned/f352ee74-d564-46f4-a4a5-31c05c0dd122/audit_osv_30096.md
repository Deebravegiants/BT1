# [H] i40e: Fix macvlan leak by synchronizing access to mac_filter_hash

## Summary
Severity: High
Advisory: CVE-2024-50041
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50041
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.168, >=5.16.0 <6.1.113, >=5.19.0 <6.6.57, >=6.2.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: Fix macvlan leak by synchronizing access to mac_filter_hash

This patch addresses a macvlan leak issue in the i40e driver caused by
concurrent access to vsi->mac_filter_hash. The leak occurs when multiple
threads attempt to modify the mac_filter_hash simultaneously, leading to
inconsistent state and potential memory leaks.

To fix this, we now wrap the calls to i40e_del_mac_filter() and zeroing
vf->default_lan_addr.addr with spin_lock/unlock_bh(&vsi->mac_filter_hash_lock),
ensuring atomic operations and preventing concurrent access.

Additionally, we add lockdep_assert_held(&vsi->mac_filter_hash_lock) in
i40e_add_mac_filter() to help catch similar issues in the future.

Reproduction steps:
1. Spawn VFs and configure port vlan on them.
2. Trigger concurrent macvlan operations (e.g., adding and deleting
	portvlan and/or mac filters).
3. Observe the potential memory leak and inconsistent state in the
	mac_filter_hash.

This synchronization ensures the integrity of the mac_filter_hash and prevents
the described leak.

## References
- https://git.kernel.org/stable/c/703c4d820b31bcadf465288d5746c53445f02a55
- https://git.kernel.org/stable/c/8831abff1bd5b6bc8224f0c0671f46fbd702b5b2
- https://git.kernel.org/stable/c/9a9747288ba0a9ad4f5c9877f18dd245770ad64e
- https://git.kernel.org/stable/c/9db6ce9e2738b05a3672aff4d42169cf3bb5a3e3
- https://git.kernel.org/stable/c/dac6c7b3d33756d6ce09f00a96ea2ecd79fae9fb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50041.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

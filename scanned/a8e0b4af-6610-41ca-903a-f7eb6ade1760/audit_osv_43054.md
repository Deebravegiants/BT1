# [H] bridge: stp: Fix a potential use-after-free when deleting a bridge

## Summary
Severity: High
Advisory: CVE-2026-72389
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72389
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bridge: stp: Fix a potential use-after-free when deleting a bridge

The three STP timers are not supposed to be armed while the bridge is
administratively down. They are synchronously deactivated when the
bridge is put administratively down and the various call sites check for
'IFF_UP' before arming them.

This check is missing from br_topology_change_detection() and it is
possible to engineer a situation in which the topology change timer is
armed while the bridge is administratively down, resulting in a
use-after-free [1] when the bridge is deleted.

Fix by adding the missing check and for good measures synchronously
shutdown the three timers when the bridge is deleted.

[1]
ODEBUG: free active (active state 0) object: ffff88811662b9b0 object type: timer_list hint: br_topology_change_timer_expired (net/bridge/br_stp_timer.c:120)
WARNING: lib/debugobjects.c:629 at debug_print_object+0x1bc/0x450, CPU#9: ip/359

## References
- https://git.kernel.org/stable/c/297a747f59bff6573196d7236178144d66524e68
- https://git.kernel.org/stable/c/2a00517db8de4be7df3d483b215c5544fb30a191
- https://git.kernel.org/stable/c/39283907a25e5caf0f2bd2947f6e56644b01e2b7
- https://git.kernel.org/stable/c/40cbfa3a28e0919469d1b086629bb3ce38a83593
- https://git.kernel.org/stable/c/4c40eec06eeac37c58e47a6058eb32901218d5d4
- https://git.kernel.org/stable/c/b4b3458ef88df4798632619f018791d4344bcd92
- https://git.kernel.org/stable/c/c86579b0a2d201792bcb59316629f4ba4758cfc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

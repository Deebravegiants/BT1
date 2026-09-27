# [H] batman-adv: mcast: fix use-after-free in orig_node RCU release

## Summary
Severity: High
Advisory: CVE-2026-64096
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64096
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: mcast: fix use-after-free in orig_node RCU release

batadv_mcast_purge_orig() removes entries from RCU-protected hlists but
does not wait for an RCU grace period before returning. Concurrent RCU
readers may still accesses references to those entries at the point of
removal. RCU-protected readers trying to operate on entries like
orig->mcast_want_all_ipv6_node will then access already freed memory.

Fix this by moving batadv_mcast_purge_orig() to batadv_orig_node_release(),
just before the call_rcu() invocation. This ensures RCU readers that were
active at purge time have drained before the orig_node memory is reclaimed.

## References
- https://git.kernel.org/stable/c/20c2d6a20ca936f5aaa6dd40f73f262ac45c87cc
- https://git.kernel.org/stable/c/70bcb678561f0fb58f33270fc73f12f3be72b878
- https://git.kernel.org/stable/c/78a63fb2f7d5630d1c1f2859a20d4e4226863b41
- https://git.kernel.org/stable/c/8a3707653ab658e082ccd992e92594e01b09a3fc
- https://git.kernel.org/stable/c/aef897c9d2dd0d9339167fb82b62beff68d076cb
- https://git.kernel.org/stable/c/ced48f55bac73f0822eae90509e51b42b4f646c8
- https://git.kernel.org/stable/c/edfb1e094104a50f931553dc82ac59246569fd32
- https://git.kernel.org/stable/c/ff3a4487ead475e27b43280b8ee3d8464fe280e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64096.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

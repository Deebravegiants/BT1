# [H] libceph: Reject monmaps advertising zero monitors

## Summary
Severity: High
Advisory: CVE-2026-68155
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68155
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Reject monmaps advertising zero monitors

A message of type CEPH_MSG_MON_MAP contains a monmap that is sent from a
monitor to the client. This monmap contains information about the
existing monitors in the cluster. Currently, a monmap indicating that
there are zero monitors in the cluster is treated as valid. However, it
is impossible to have zero monitors in the cluster and still receive a
valid monmap from a monitor. Therefore, such a monmap must be corrupted
and should be treated as invalid. Furthermore, a monmap with a monitor
count of zero can subsequently crash the client when attempting to open
a session with a monitor in __open_session(). This happens because the
"BUG_ON(monc->monmap->num_mon < 1)" assertion in pick_new_mon() is
triggered.

This patch extends a check in ceph_monmap_decode() to also reject
arriving mon_maps with num_mon == 0 rather than only with
num_mon > CEPH_MAX_MON.

[ idryomov: drop "log output for unusual values of num_mon" part ]

## References
- https://git.kernel.org/stable/c/0591a15815b498be628a937146e44487d599ba33
- https://git.kernel.org/stable/c/3b249546f59c3d6d3592c10657f82bc3f1faa07c
- https://git.kernel.org/stable/c/40480eee361ed9676b3f844d532ac28b47251634
- https://git.kernel.org/stable/c/caf082ef8609a6ac26159ce115f55ab7d00231a3
- https://git.kernel.org/stable/c/cd0d41bc569632eaaeccde9d2a6bc919ec00c407
- https://git.kernel.org/stable/c/e3ccd4ecab09b22f507f49cb7ed9990c7158ceab
- https://git.kernel.org/stable/c/e67e8b694872c9bc66996040f9de9242f6236ed9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68155.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [C] batman-adv: tp_meter: avoid use of uninit sender vars

## Summary
Severity: Critical
Advisory: CVE-2026-52931
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52931
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tp_meter: avoid use of uninit sender vars

batadv_tp_recv_ack() and batadv_tp_stop() are only valid for tp_vars in the
BATADV_TP_SENDER role. When called with a BATADV_TP_RECEIVER role, it
proceeds to read sender-only members that were never initialized, leading
to undefined behavior.

This can be triggered when a node that is currently acting as a receiver in
an ongoing tp_meter session receives a malicious ACK packet.

Guard against this by checking tp_vars->role immediately after the
lookup and bailing out if it is not BATADV_TP_SENDER, before any of
those members are accessed.

## References
- https://git.kernel.org/stable/c/0e388af04b3958b178a1b979527f93eb46ea1fee
- https://git.kernel.org/stable/c/1a21c055f66e78973712a4a1be2a554f1ee2e4f4
- https://git.kernel.org/stable/c/53f931e0146ae5bdab4cba302646827d06b3794b
- https://git.kernel.org/stable/c/6c65cf23d4c6170fcf5714c32aa64689718cb142
- https://git.kernel.org/stable/c/85397e48afe6be83ffca5ad3f4792296bfc81d3d
- https://git.kernel.org/stable/c/9884c9c02d3c90e9215db3c5128f59045d20ae91
- https://git.kernel.org/stable/c/dc2ae5fbd2dadc26735092f140b246841d969a11
- https://git.kernel.org/stable/c/ecdaa3e4d91040206afe21bc8a0d1198a0971ff3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52931.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52931
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

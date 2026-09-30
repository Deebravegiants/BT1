# [H] ibmveth: Disable GSO for packets with small MSS

## Summary
Severity: High
Advisory: CVE-2026-46273
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46273
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ibmveth: Disable GSO for packets with small MSS

Some physical adapters on Power systems do not support segmentation
offload when the MSS is less than 224 bytes. Attempting to send such
packets causes the adapter to freeze, stopping all traffic until
manually reset.

Implement ndo_features_check to disable GSO for packets with small MSS
values. The network stack will perform software segmentation instead.

The 224-byte minimum matches ibmvnic
commit <f10b09ef687f> ("ibmvnic: Enforce stronger sanity checks
on GSO packets")
which uses the same physical adapters in SEA configurations.

The issue occurs specifically when the hardware attempts to perform
segmentation (gso_segs > 1) with a small MSS. Single-segment GSO packets
(gso_segs == 1) do not trigger the problematic LSO code path and are
transmitted normally without segmentation.

Add an ndo_features_check callback to disable GSO when MSS < 224 bytes.
Also call vlan_features_check() to ensure proper handling of VLAN packets,
particularly QinQ (802.1ad) configurations where the hardware parser may
not support certain offload features.

Validated using iptables to force small MSS values. Without the fix,
the adapter freezes. With the fix, packets are segmented in software
and transmission succeeds. Comprehensive regression testing completedd
(MSS tests, performance, stability).

## References
- https://git.kernel.org/stable/c/1cdf5dbcec988d06f5f720bdf89e91073f77fa10
- https://git.kernel.org/stable/c/3af24f0c4c31f18a4a2d927990759194832bb6e9
- https://git.kernel.org/stable/c/82bc89fbb82d9396fb4eaee8720ea85e2e787957
- https://git.kernel.org/stable/c/86fc64584811d43c9ccd74447de58620189d8b77
- https://git.kernel.org/stable/c/9a5e984d7af910e46dcbed3ce77873e000a4f77d
- https://git.kernel.org/stable/c/c1f261863e65b508f37416dfbc5c5d911c9b9233
- https://git.kernel.org/stable/c/cc427d24ac6442ffdeafd157a63c7c5b73ed4de4
- https://git.kernel.org/stable/c/db8012c631cb845e9ae2b4b531e17d86c9519755
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46273.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

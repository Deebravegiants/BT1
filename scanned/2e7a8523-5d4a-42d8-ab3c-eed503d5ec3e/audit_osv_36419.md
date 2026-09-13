# [H] igc: fix page fault in XDP TX timestamps handling

## Summary
Severity: High
Advisory: CVE-2026-23445
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23445
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

igc: fix page fault in XDP TX timestamps handling

If an XDP application that requested TX timestamping is shutting down
while the link of the interface in use is still up the following kernel
splat is reported:

[  883.803618] [   T1554] BUG: unable to handle page fault for address: ffffcfb6200fd008
...
[  883.803650] [   T1554] Call Trace:
[  883.803652] [   T1554]  <TASK>
[  883.803654] [   T1554]  igc_ptp_tx_tstamp_event+0xdf/0x160 [igc]
[  883.803660] [   T1554]  igc_tsync_interrupt+0x2d5/0x300 [igc]
...

During shutdown of the TX ring the xsk_meta pointers are left behind, so
that the IRQ handler is trying to touch them.

This issue is now being fixed by cleaning up the stale xsk meta data on
TX shutdown. TX timestamps on other queues remain unaffected.

## References
- https://git.kernel.org/stable/c/31521c124e6488c4a81658e35199feb75a988d86
- https://git.kernel.org/stable/c/45b33e805bd39f615d9353a7194b2da5281332df
- https://git.kernel.org/stable/c/5e4c90c94eb766d70e30694b7fe66862aabaf24b
- https://git.kernel.org/stable/c/b02fa17d1744d19cd3820bdbf6ec5d85547977bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23445
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

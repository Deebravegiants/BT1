# [H] drm/vc4: Zero the tile state data array before each BIN job

## Summary
Severity: High
Advisory: CVE-2026-74453
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74453
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vc4: Zero the tile state data array before each BIN job

The binner BO is a single 16MB buffer split into 512KB slots that are
handed out to jobs at submission time and recycled as jobs complete,
without ever being cleared. Each slot holds the job's Tile State Data
Array (TSDA) at its start, followed by the tile allocation pool.

While the tile allocation pool is only walked by the render thread
through branches the binner generated during the current job, the
TSDA is the PTB's own per-tile bookkeeping and is consumed by the
hardware itself. Although the kernel sets the "Auto-initialise Tile
State Data Array" flag in the tile binning mode configuration, the
PTB demonstrably still acts on stale tile state left by the slot's
previous user: the binner ends up creating invalid command streams
with invalid primitive streams and branches, which can cause GPU hangs
as observed in [1][2].

Zero the TSDA when the job's binning slot is configured. This clears
48 bytes per tile (~24KB for a 1080p frame) in the submission path, and
guarantees the PTB never sees another job's tile state.

The tile count is only checked for being non-zero today, so the 8-bit
fields it comes from can describe a tile state array almost six times
larger than the slot it has to live in. Bound it before the slot is
handed out, since such size decides how much of the slot is left for
the tile alloc pool.

## References
- https://git.kernel.org/stable/c/0e858422df2334165293ea742da9fbb2e51f2739
- https://git.kernel.org/stable/c/48a570c964d8e37d353381e4195106277e17f5cb
- https://git.kernel.org/stable/c/57667eb7548faaac396c6e39f3b4444dab5b097c
- https://git.kernel.org/stable/c/a75c8f365e209aa9bb927b0942a7840152d44892
- https://git.kernel.org/stable/c/c5d8e8e1a8e3b4e464683c5a8a869c16a6382fea
- https://git.kernel.org/stable/c/c8dea7e7c6098e383e44f21a64d0431da5480e3f
- https://git.kernel.org/stable/c/d3677372e0275e139f0efd2872c5a524b5d12868
- https://git.kernel.org/stable/c/f5802be65535f8818af7191159cf8c11f48ab2a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74453.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] nvdimm/btt: Handle preemption in BTT lane acquisition

## Summary
Severity: High
Advisory: CVE-2026-74365
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74365
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvdimm/btt: Handle preemption in BTT lane acquisition

BTT lanes serialize access to per-lane metadata and workspace state
during BTT I/O. The btt-check unit test reports data mismatches during
BTT writes due to a race in lane acquisition that can lead to silent
data corruption.

The existing lane model uses a spinlock together with a per-CPU
recursion count. That recursion model stopped being valid after BTT
lanes became preemptible: another task can run on the same CPU,
observe a non-zero recursion count, bypass locking, and use the same
lane concurrently.

BTT lanes are also held across arena_write_bytes() calls. That path
reaches nsio_rw_bytes(), which flushes writes with nvdimm_flush().
Some provider flush callbacks can sleep, making a spinlock the wrong
primitive for the lane lifetime.

Replace the spinlock-based recursion model with a dynamically
allocated per-lane mutex array and take the lane lock
unconditionally.

Add might_sleep() to catch any future atomic-context caller.

Found with the ndctl unit test btt-check.sh.

## References
- https://git.kernel.org/stable/c/417918783bcfe0be135019df16a267b3af442efd
- https://git.kernel.org/stable/c/4eafa810b042d985ec6bbf5b514414e73cee6f6f
- https://git.kernel.org/stable/c/5c53406098b599c420b031e6ec5ba8a2f3794c50
- https://git.kernel.org/stable/c/73e35c1bdfa160b41fdbe204e02325f0687de506
- https://git.kernel.org/stable/c/8d4b989d9c9afe5f185aa5853b666fc4617afe9e
- https://git.kernel.org/stable/c/fd7a97b2514cfc4b4cc067a27dd39bde2a8b1735
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74365.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

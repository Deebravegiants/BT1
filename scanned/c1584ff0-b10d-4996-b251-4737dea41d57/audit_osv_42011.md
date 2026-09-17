# [H] partitions: aix: bound the pp_count scan to the ppe array

## Summary
Severity: High
Advisory: CVE-2026-64318
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64318
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

partitions: aix: bound the pp_count scan to the ppe array

aix_partition() reads the physical volume descriptor into a fixed-size
struct pvd and then scans its physical-partition-extent array:

	int numpps = be16_to_cpu(pvd->pp_count);
	...
	for (i = 0; i < numpps; i += 1) {
		struct ppe *p = pvd->ppe + i;
		...
		lp_ix = be16_to_cpu(p->lp_ix);

pvd points at a single kmalloc()'d struct pvd whose ppe[] member holds a
fixed ARRAY_SIZE(pvd->ppe) (1016) entries, but the loop runs up to the
on-disk pp_count.  pp_count is an unvalidated __be16 read straight from
the descriptor, so a crafted AIX image with pp_count larger than 1016
drives the loop to read pvd->ppe[i] past the end of the allocation (up
to 65535 entries, ~2 MB out of bounds).

The partition scan runs without mounting anything, when a block device
with a crafted AIX/IBM partition table appears (an attacker-supplied
image attached with losetup -P, or a device auto-scanned by udev), via
msdos_partition() -> aix_partition().

Clamp the scan to the number of entries the ppe[] array can hold.

## References
- https://git.kernel.org/stable/c/09861651617ba0fec089e8b9477439e68398c110
- https://git.kernel.org/stable/c/2dc0bfd2fe355fb930de63c2f2eb8ced8570c579
- https://git.kernel.org/stable/c/44f37ee92fdcd377c41bdf6a31cdd8cc7d4c410e
- https://git.kernel.org/stable/c/4671bb74bba05fdd4acf670a35758c29e8c97b83
- https://git.kernel.org/stable/c/5eacdb1967378f5e5591cd27a2d8cdee2df1a599
- https://git.kernel.org/stable/c/b5e9c09309e18fd9839ad007c238120353ca0cc4
- https://git.kernel.org/stable/c/ce93228e2193a17d2c58b656e439bb39fe5c3af8
- https://git.kernel.org/stable/c/fd94a779020f2ecc8b2607f4c20b34acb1763b9a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64318.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

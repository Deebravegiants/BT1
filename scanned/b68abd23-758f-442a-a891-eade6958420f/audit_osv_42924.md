# [H] ocfs2: avoid moving extents to occupied clusters

## Summary
Severity: High
Advisory: CVE-2026-72164
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72164
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: avoid moving extents to occupied clusters

For non-auto OCFS2_IOC_MOVE_EXT operations, userspace supplies a physical
me_goal.  ocfs2_move_extent() initializes new_phys_cpos from that goal and
expects ocfs2_probe_alloc_group() to replace it with a free run in the
target block group.

The probe currently leaves *phys_cpos unchanged if the scan reaches the
end of the group without finding a free run.  An occupied goal at the last
bit can therefore survive the probe and be passed to
__ocfs2_move_extent(), which copies file data into a cluster still owned
by another inode before the bitmap is updated.

When the probe does find a free run, it also subtracts move_len from the
ending bit.  The start of an N-bit run ending at i is i - N + 1, so the
current calculation can report the bit immediately before the free run.

Clear *phys_cpos before scanning and use the correct free-run start. 
Callers already treat a zero result as -ENOSPC, so failed probes no longer
continue with an occupied caller-controlled goal.

## References
- https://git.kernel.org/stable/c/0d0c5c17b18bdbc592ac26ab4d1de7e3dbf9be1e
- https://git.kernel.org/stable/c/19f7b04924b20b81dabbeed19d5542792ba5b6d6
- https://git.kernel.org/stable/c/22920541c35a9f23f219038ba5874c843a7c4419
- https://git.kernel.org/stable/c/3112afebf2a76e522fbaabcbb0c47aafbdc35932
- https://git.kernel.org/stable/c/35486b291b8fbde6c4d0b1c79e565c6260d3329d
- https://git.kernel.org/stable/c/4d1953d3aeb4a7f6623083e1839068ee1c157db2
- https://git.kernel.org/stable/c/d5d5a21fb33cd9b963aea99da81e4dacd452cd95
- https://git.kernel.org/stable/c/e281d892ce5870a50fdc718cb3bfc3dd5b62c728
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72164.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72164
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

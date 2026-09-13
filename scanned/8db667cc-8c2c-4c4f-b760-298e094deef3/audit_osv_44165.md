# [H] xfs: fix exchange-range reflink flag clearing issue with INO1_WRITTEN

## Summary
Severity: High
Advisory: CVE-2026-80530
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80530
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: fix exchange-range reflink flag clearing issue with INO1_WRITTEN

When exchanging two full-file ranges, xmi_can_exchange_reflink_flags()
can move the reflink inode flag from the file that currently has it to
the other file, as long as exactly one side is marked.  This assumes
that the file contents, and therefore all shared extents, are exchanged.

That assumption is not true when XFS_EXCHMAPS_INO1_WRITTEN is set.
xfs_exchmaps_can_skip_mapping() can skip hole and unwritten mappings
from file1, so an exchange can complete without moving every mapping
that the earlier flag-swap decision accounted for.  In that case the
post-operation cleanup can clear the reflink flag from an inode that
still owns shared written extents.  Later writes then take the
non-reflink write path and may update blocks that should still have
been protected by CoW, which shows up as data corruption between
reflink-related files.

Fix this by disabling the reflink flag exchange whenever
XFS_EXCHMAPS_INO1_WRITTEN is requested.  The contents exchange can still
proceed; the conservative outcome is that both inodes keep the reflink
flag.  The regular reflink flag cleanup path can drop the extra flag
later once the inode no longer has shared extents.

## References
- http://www.openwall.com/lists/oss-security/2026/09/03/1
- https://git.kernel.org/stable/c/03c9c9116e6da641424681f705698d7f5e2128e0
- https://git.kernel.org/stable/c/0f27b22343b63e10773e6781344640c2c753eec3
- https://git.kernel.org/stable/c/2efbd8890b53f4756fdc7b0ef346fa514ffb7d66
- https://git.kernel.org/stable/c/b2d5a81dae385333f9734910277fbf94c78bd17f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80530.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80530
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

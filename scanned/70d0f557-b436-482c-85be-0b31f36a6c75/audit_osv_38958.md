# [H] xfs: delete attr leaf freemap entries when empty

## Summary
Severity: High
Advisory: CVE-2026-43187
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43187
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: delete attr leaf freemap entries when empty

Back in commit 2a2b5932db6758 ("xfs: fix attr leaf header freemap.size
underflow"), Brian Foster observed that it's possible for a small
freemap at the end of the end of the xattr entries array to experience
a size underflow when subtracting the space consumed by an expansion of
the entries array.  There are only three freemap entries, which means
that it is not a complete index of all free space in the leaf block.

This code can leave behind a zero-length freemap entry with a nonzero
base.  Subsequent setxattr operations can increase the base up to the
point that it overlaps with another freemap entry.  This isn't in and of
itself a problem because the code in _leaf_add that finds free space
ignores any freemap entry with zero size.

However, there's another bug in the freemap update code in _leaf_add,
which is that it fails to update a freemap entry that begins midway
through the xattr entry that was just appended to the array.  That can
result in the freemap containing two entries with the same base but
different sizes (0 for the "pushed-up" entry, nonzero for the entry
that's actually tracking free space).  A subsequent _leaf_add can then
allocate xattr namevalue entries on top of the entries array, leading to
data loss.  But fixing that is for later.

For now, eliminate the possibility of confusion by zeroing out the base
of any freemap entry that has zero size.  Because the freemap is not
intended to be a complete index of free space, a subsequent failure to
find any free space for a new xattr will trigger block compaction, which
regenerates the freemap.

It looks like this bug has been in the codebase for quite a long time.

## References
- https://git.kernel.org/stable/c/479b05fc3ee272090f671b06a41f3da8aa78eece
- https://git.kernel.org/stable/c/6f13c1d2a6271c2e73226864a0e83de2770b6f34
- https://git.kernel.org/stable/c/a631899025d47ea1aa6464d76db5b4d3b6d196fd
- https://git.kernel.org/stable/c/aa9083d97e2157da3c6fb45ddb1a97af7f188f7f
- https://git.kernel.org/stable/c/e1b8c6452ee99a30e188a88f3f3f804fb1c6004a
- https://git.kernel.org/stable/c/f31a8334e1c54b126fcecf98645a49b6bc5ad399
- https://git.kernel.org/stable/c/f3c0d1fc1eadbb4adbee5ab7757d41d35f48325b
- https://git.kernel.org/stable/c/ffaf5c99d0f862db021fb1af8b813c1416b1beb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43187.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

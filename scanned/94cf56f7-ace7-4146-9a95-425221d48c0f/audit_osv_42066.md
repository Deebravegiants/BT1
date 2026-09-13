# [H] fs/ntfs3: validate Dirty Page Table capacity in log_replay copy_lcns

## Summary
Severity: High
Advisory: CVE-2026-64432
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64432
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: validate Dirty Page Table capacity in log_replay copy_lcns

In the analysis pass of $LogFile journal replay, log_replay() copies
LCNs from each action log record into an existing Dirty Page Table
(DPT) entry without bounding the destination index. A crafted NTFS
image with DPT entry lcns_follow=1 and an action log record with
lcns_follow=2 produces a kernel slab out-of-bounds write at mount
time:

  BUG: KASAN: slab-out-of-bounds in log_replay+0x654c/0xdb60
  Write of size 8 at addr ffff8880095e1040 by task mount

Two attacker-controlled fields can drive j+i past the allocated
page_lcns[] array:

  1. dp->lcns_follow (capacity) can be smaller than lrh->lcns_follow.
  2. lrh->target_vcn may be smaller than dp->vcn, making the u64
     subtraction wrap to a huge size_t.

Validate target VCN delta and per-record LCN count against the
DPT entry capacity, bail via the existing out: cleanup label with
-EINVAL.

This mirrors the bounds-check pattern added in commit b2bc7c44ed17
("fs/ntfs3: Fix slab-out-of-bounds read in DeleteIndexEntryRoot")
and commit 0ca0485e4b2e ("fs/ntfs3: validate rec->used in
journal-replay file record check").

## References
- https://git.kernel.org/stable/c/3aa96956ca2200674e2a8f9c23ec6ecd45e5010f
- https://git.kernel.org/stable/c/57382ec6ac63b63dce2789e835fded28b698ae79
- https://git.kernel.org/stable/c/946046841013ebac8492ef49651c53638d7a9a6a
- https://git.kernel.org/stable/c/964c3fae1dfc49dde5468eace940f199cda234e9
- https://git.kernel.org/stable/c/c6f9e804f73ef809529865fbc7256dd189ff8c33
- https://git.kernel.org/stable/c/cf28fc1658463d768657cf1c27a83980d4ba7ef2
- https://git.kernel.org/stable/c/f433acc85b86f327d03ba8b03a33c105c51053de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64432
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] fs/ntfs3: bound copy_lcns dp->page_lcns[] index in analysis pass

## Summary
Severity: High
Advisory: CVE-2026-72196
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72196
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: bound copy_lcns dp->page_lcns[] index in analysis pass

In log_replay()'s analysis pass, after find_dp() returns a
valid DIR_PAGE_ENTRY for the (target_attr, target_vcn) tuple,
the copy_lcns block walks lrh->lcns_follow further entries:

	t16 = le16_to_cpu(lrh->lcns_follow);
	for (i = 0; i < t16; i++) {
	    size_t j = (size_t)(le64_to_cpu(lrh->target_vcn) -
	                        le64_to_cpu(dp->vcn));
	    dp->page_lcns[j + i] = lrh->page_lcns[i];
	}

find_dp() only validates that target_vcn falls within
[dp->vcn, dp->vcn + dp->lcns_follow), i.e., that the FIRST
cluster is covered.  The walk through the further entries is
not bounded against dp->lcns_follow.  For a malformed LRH
where target_vcn = dp->vcn + dp->lcns_follow - 1 and
lrh->lcns_follow > 1, the i > 0 writes overflow the dp's
allocated page_lcns[] array.

Add the missing j + lrh->lcns_follow <= dp->lcns_follow guard.

Reproduced under UML+KASAN on mainline 8d90b09e6741 as a
slab-out-of-bounds write of size 8 from log_replay+0x68d4 on
the mount path.

This is distinct from Pavitra Jha's 2026-05-02 patch
("fs/ntfs3: validate lcns_follow in log_replay conversion",
<20260502154252.164586-1-jhapavitra98@gmail.com>) which
addresses the separate version-0 dirty-page-table conversion
path's memmove(&dp->vcn, ...) call.  The two fixes are
complementary; both should land.

[almaz.alexandrovich@paragon-software.com: clang-formatted the changes,
fixed conflicts]

## References
- https://git.kernel.org/stable/c/0f13e823bf86bd1800168ea0bb5bca8b8500a81c
- https://git.kernel.org/stable/c/49c86dae0c0ccb8d98ddcdc46987259389c816dd
- https://git.kernel.org/stable/c/5e7b598660cfa8e5af172cf4c65cffc126333307
- https://git.kernel.org/stable/c/9b3d8cc9d54fcded4de51b2b1026ae7182512077
- https://git.kernel.org/stable/c/9b7c28d8c61bdb041936222a09a708531a1c2921
- https://git.kernel.org/stable/c/d240cd98f5f7b65c90f6b2b6abe3232ccdc405ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72196.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72196
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

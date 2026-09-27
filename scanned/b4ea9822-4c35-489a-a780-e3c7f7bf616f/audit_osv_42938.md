# [H] fs/ntfs3: bound attr_off in UpdateResidentValue against data_off

## Summary
Severity: High
Advisory: CVE-2026-72195
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72195
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: bound attr_off in UpdateResidentValue against data_off

In do_action()'s UpdateResidentValue case (fslog.c:3307),
lrh->attr_off and lrh->redo_len come from the on-disk LRH.
When they satisfy aoff + dlen < attr->res.data_off, the
assignment

	attr->res.data_size = cpu_to_le32(aoff + dlen - data_off);

underflows to ~4 GiB (e.g. 0xFFFFFFF9 when aoff=0x10, dlen=1,
data_off=0x18).  Subsequent code that reads attr->res.data_size
to walk the resident attribute payload would then read up to
4 GiB past the 1024-byte MFT record allocation.

The existing mi_enum_attr() defense in fs/ntfs3/record.c:287
catches the corrupted data_size on the next attribute walk
and fails the mount, but only on the path that walks all
attributes.  A read site that picks an attribute by name and
reads its data_size without re-validating is not covered.
Validate aoff against data_off and asize at the source.

Reproduced under UML+KASAN on mainline 8d90b09e6741 via
pr_warn-only probe: with aoff=0x10 and data_off=0x18, the
post-assignment data_size is 0xfffffff9 (mount then fails
at -22 from mi_enum_attr).

[almaz.alexandrovich@paragon-software.com: clang-formatted the changes]

## References
- https://git.kernel.org/stable/c/50b5e83384e7fed3d11d18b79ff350e9d6d89861
- https://git.kernel.org/stable/c/53c12f178f584dc5f836ffe2782138a6e9348ed9
- https://git.kernel.org/stable/c/546518468e6c9ea469669eef78f8cc380ad6e2ca
- https://git.kernel.org/stable/c/97758fd9756b5f09e9ddc6a5f6a569041acc8421
- https://git.kernel.org/stable/c/a89c66674283a0293c0f266dc57087a6114371a3
- https://git.kernel.org/stable/c/ab8761676d638c5be170aaf91b7ffdd451236616
- https://git.kernel.org/stable/c/d1570c48f49a693974d000251030370ee2e83539
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72195.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72195
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

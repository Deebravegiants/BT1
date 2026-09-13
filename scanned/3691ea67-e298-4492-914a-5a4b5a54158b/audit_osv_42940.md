# [H] fs/ntfs3: bound DeleteIndexEntryAllocation memmove length

## Summary
Severity: High
Advisory: CVE-2026-72197
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72197
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: bound DeleteIndexEntryAllocation memmove length

In do_action()'s DeleteIndexEntryAllocation case, e->size comes
from an on-disk INDEX_BUFFER entry.  When e->size makes
e + e->size point past hdr + hdr->used,
PtrOffset(e1, Add2Ptr(hdr, used)) returns a negative ptrdiff_t
that is silently cast to a quasi-infinite size_t when passed
to memmove().  The memmove then walks past the destination
buffer.

The sibling DeleteIndexEntryRoot case at fslog.c:3540-3543
already carries the corresponding guard:

	if (PtrOffset(e1, Add2Ptr(hdr, used)) < esize ||
	    Add2Ptr(e, esize) > Add2Ptr(lrh, rec_len) ||
	    used + esize > le32_to_cpu(hdr->total)) {
		goto dirty_vol;
	}

Apply the same shape to the allocation-path case.  Also reject
esize == 0: memmove(e, e, ...) is a no-op and leaves
hdr->used unchanged, hiding a malformed entry from the
existing check_index_header() walk.

Reproduced under UML+KASAN on mainline 8d90b09e6741 by
mounting a crafted NTFS image: the unguarded memmove takes a
length of 0xffffffffffffff00 and the kernel oopses in
memmove+0x81/0x1a0 on the do_action+0x36a2 frame.

[almaz.alexandrovich@paragon-software.com: clang-formatted the changes]

## References
- https://git.kernel.org/stable/c/09fddd52c1b0cef2c086d61be8f3d5dc92e36565
- https://git.kernel.org/stable/c/4c8aac931c1cd70347961ba5157aa916448c6a25
- https://git.kernel.org/stable/c/554700c65d398276cb00a8ef95f1d5e00b9eff93
- https://git.kernel.org/stable/c/b509b9613f20dc5b653d54bf78fab00d79cc43c8
- https://git.kernel.org/stable/c/c38ed2ab62fab75fd6d0fdc2bee540fbebc7b959
- https://git.kernel.org/stable/c/f383aae59ec3994c14804f4191c59038b206be81
- https://git.kernel.org/stable/c/fc4626bb3656362de8b0ecd56605d47a19ec3518
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72197.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

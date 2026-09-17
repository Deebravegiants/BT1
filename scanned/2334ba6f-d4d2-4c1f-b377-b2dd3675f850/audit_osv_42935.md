# [C] ntfs3: validate split-point offset in indx_insert_into_buffer

## Summary
Severity: Critical
Advisory: CVE-2026-72191
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72191
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs3: validate split-point offset in indx_insert_into_buffer

indx_insert_into_buffer() computes

    used = used1 - to_copy - sp_size;
    memmove(de_t, Add2Ptr(sp, sp_size), used - le32_to_cpu(hdr1->de_off));

where sp and sp_size come from hdr_find_split().  hdr_find_split()
walks entries by le16_to_cpu(e->size) without validating that each
step stays within hdr->used or that the size field is at least
sizeof(struct NTFS_DE).  index_hdr_check(), the on-load gatekeeper,
only validates header-level fields (used, total, de_off) and does
not walk per-entry sizes.

A crafted NTFS image whose leaf INDEX_HDR reports used == total but
contains one interior NTFS_DE with size = 0xFFF0 therefore passes
validation, descends to indx_insert_into_buffer() through the
ntfs_create() -> indx_insert_entry() path, and makes hdr_find_split()
return an sp whose sp_size (0xFFF0) greatly exceeds the remaining
bytes in the buffer.  The u32 subtraction underflows and the memmove
count becomes a near-4-GiB value, producing an out-of-bounds kernel
write that corrupts adjacent allocations and panics the kernel.

Reproduced on 7.0.0-rc7 with UML + KASAN via a crafted image and a
single 'touch' inside the mounted directory; crash site resolves to
fs/ntfs3/index.c at the memmove.  Trigger requires only local mount
of an attacker-supplied filesystem image (USB, loopback, or removable
media auto-mount).

Reject the split whenever the chosen sp plus its declared size
already extends past hdr1->used.  This is the minimal fix; it
preserves the existing hdr_find_split() contract and relies on the
same out: cleanup path as the pre-existing error returns.

A prior OOB read in the very same indx_insert_into_buffer() memmove
was fixed in commit b8c44949044e ("fs/ntfs3: Fix OOB read in
indx_insert_into_buffer") by tightening hdr_find_e(), but that fix
does not cover the split-point size field path addressed here: sp is
returned by hdr_find_split(), not hdr_find_e(), and the underflow is
driven by sp->size rather than hdr->used exceeding hdr->total.

## References
- https://git.kernel.org/stable/c/1758a564b6ebe7f4a82f23c9851d1cae15549457
- https://git.kernel.org/stable/c/4c2f648139a0a86f4486170f72e24fedd4fae74e
- https://git.kernel.org/stable/c/7bf74e6baf810fe325f111996496c678fc6e244f
- https://git.kernel.org/stable/c/8e4ba5a38c155bb3c1c11e63cd285b178cdb099e
- https://git.kernel.org/stable/c/b232eb5c9fe11ec2368e9b565db69c724c35fbd2
- https://git.kernel.org/stable/c/f1df9d771df47aa40de6d70949c28720ae1e430d
- https://git.kernel.org/stable/c/f3624cc069195001c88df7a291af215f2133ff2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

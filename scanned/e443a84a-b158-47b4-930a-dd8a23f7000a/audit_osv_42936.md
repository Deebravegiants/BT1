# [C] ntfs3: bound to_move in indx_insert_into_root before hdr_insert_head

## Summary
Severity: Critical
Advisory: CVE-2026-72192
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72192
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs3: bound to_move in indx_insert_into_root before hdr_insert_head

indx_insert_into_root() promotes a full resident $INDEX_ROOT into
$INDEX_ALLOCATION and copies all non-last resident root entries into
a newly allocated INDEX_BUFFER via hdr_insert_head(). The source
byte count 'to_move' is summed from the on-disk resident entry sizes
and is independent of the destination buffer size, which comes from
root->index_block_size (via indx->index_bits).

A crafted NTFS image that keeps a valid, full resident root but
shrinks root->index_block_size down to 512 after the root has been
populated makes hdr_insert_head() memcpy attacker-controlled resident
entry bytes past the end of the kmalloc(1u << indx->index_bits)
allocation returned by indx_new(). For a 512-byte destination and a
resident root whose non-last entries total 560 bytes, the memcpy
overruns by 120 bytes and a following memmove extends the highest
written offset to 136 bytes past the allocation. The overflow bytes
are a direct copy of on-disk entries (via kmemdup), so they are
fully attacker-controlled.

The write is reachable from unprivileged open(O_CREAT) on a mounted
crafted NTFS image: a single sufficiently long create in a directory
whose resident root is already full forces root promotion and
triggers the copy.

This is a controlled out-of-bounds write of 120-136 bytes past a
kmalloc(index_block_size) allocation, with attacker-controlled
content. It is a bounded adjacent-heap corruption primitive; it is
not an arbitrary-address write. Successful exploitation into a named
victim object depends on the surrounding slab layout.

Reject the copy at the sink. The destination's INDEX_HDR already
reports hdr_total (the payload capacity of the new buffer) and
hdr_used (the bytes already consumed by the terminal END entry
installed by indx_new()); require that to_move fits in the remaining
payload before calling hdr_insert_head(). On mismatch, fail with
-EINVAL and mark the filesystem as having a detected on-disk
inconsistency, which is the same behaviour as the surrounding
validation in this function.

## References
- https://git.kernel.org/stable/c/0af83b8155cc848e9f5d2c36e20a70d024214649
- https://git.kernel.org/stable/c/194b00c99ba971fa7cf6acd747a36032c6de54eb
- https://git.kernel.org/stable/c/53c5f3b2da3774b41534728aba295c098c9efa19
- https://git.kernel.org/stable/c/9b6926ac9c970ae0b2c2fe6289b16e9aa10b6a67
- https://git.kernel.org/stable/c/aaa1f956c0fc41089a4a534da7df91552a08a47c
- https://git.kernel.org/stable/c/cb3161deebcaf8d36d3115abf452c633f2180fc1
- https://git.kernel.org/stable/c/d240f5f9d036b8180224954d9873f172b6be4dd8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72192.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

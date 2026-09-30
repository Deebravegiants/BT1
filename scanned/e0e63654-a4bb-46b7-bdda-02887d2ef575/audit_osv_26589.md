# [H] scsi: mpi3mr: Use number of bits to manage bitmap sizes

## Summary
Severity: High
Advisory: CVE-2023-53376
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53376
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Use number of bits to manage bitmap sizes

To allocate bitmaps, the mpi3mr driver calculates sizes of bitmaps using
byte as unit. However, bitmap helper functions assume that bitmaps are
allocated using unsigned long as unit. This gap causes memory access beyond
the bitmap sizes and results in "BUG: KASAN: slab-out-of-bounds".  The BUG
was observed at firmware download to eHBA-9600. Call trace indicated that
the out-of-bounds access happened in find_first_zero_bit() called from
mpi3mr_send_event_ack() for miroc->evtack_cmds_bitmap.

To fix the BUG, do not use bytes to manage bitmap sizes. Instead, use
number of bits, and call bitmap helper functions which take number of bits
as arguments. For memory allocation, call bitmap_zalloc() instead of
kzalloc() and krealloc(). For memory free, call bitmap_free() instead of
kfree(). For zero clear, call bitmap_clear() instead of memset().

Remove three fields for bitmap byte sizes in struct scmd_priv which are no
longer required. Replace the field dev_handle_bitmap_sz with
dev_handle_bitmap_bits to keep number of bits of removepend_bitmap across
resize.

## References
- https://git.kernel.org/stable/c/339e61565f81a6534afdc18fd854b2e2628bf5db
- https://git.kernel.org/stable/c/6a675a6d57d31da43d8da576465c1cd5d5b0bd3d
- https://git.kernel.org/stable/c/8ac713d2e9845e9234bb12ae5903040685d5aff9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53376.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53376
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

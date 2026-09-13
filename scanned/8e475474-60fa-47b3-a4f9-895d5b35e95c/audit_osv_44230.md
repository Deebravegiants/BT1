# [H] btrfs: lzo: reject compressed segment that overflows the compressed input

## Summary
Severity: High
Advisory: CVE-2026-80631
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80631
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: lzo: reject compressed segment that overflows the compressed input

lzo_decompress_bio() validates each on-disk segment length seg_len only
against the workspace cbuf size, not against the compressed input size
(compressed_len, the total folio bytes of the bio).  A crafted extent can
carry a segment whose seg_len passes the cbuf check but runs past the end
of the bio, so copy_compressed_segment() walks off the last folio:
get_current_folio() then returns the NULL folio from bio_next_folio(), and
with CONFIG_BTRFS_ASSERT disabled (default) folio_size(NULL) faults.

 BUG: KASAN: null-ptr-deref in lzo_decompress_bio (fs/btrfs/lzo.c:383)
 Read of size 8 at addr 0000000000000000 by task kworker/u8:1/29
 Workqueue: btrfs-endio simple_end_io_work
  kasan_report (mm/kasan/report.c:590)
  lzo_decompress_bio (fs/btrfs/lzo.c:383)
  end_bbio_compressed_read (fs/btrfs/compression.c:1065)
  btrfs_bio_end_io (fs/btrfs/bio.c:135)
  btrfs_check_read_bio (fs/btrfs/bio.c:180 fs/btrfs/bio.c:285)
  simple_end_io_work
  process_one_work
  worker_thread

Reject any segment whose payload would extend beyond compressed_len before
copying it, treating it as corruption like the other on-disk validation
failures in this function.

## References
- https://git.kernel.org/stable/c/1641d058adfbd50cf95d54581ed5d142ee82c07f
- https://git.kernel.org/stable/c/b0d27d43791b7a3057c3c4aedf9b4aa033d37c46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80631.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80631
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

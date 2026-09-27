# [H] iomap: guard io_size EOF trim against concurrent truncate underflow

## Summary
Severity: High
Advisory: CVE-2026-72367
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72367
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: guard io_size EOF trim against concurrent truncate underflow

iomap: fix zero padding data issue in concurrent append writes
changed ioend accounting so that io_size tracks only valid data
within EOF.  This trims io_size when a writeback range extends
past end_pos:

    ioend->io_size += map_len;
    if (ioend->io_offset + ioend->io_size > end_pos)
        ioend->io_size = end_pos - ioend->io_offset;

However, if end_pos ends up below ioend->io_offset, the subtraction
becomes negative and is stored in size_t io_size, causing an unsigned
wrap to a huge value.  This can happen when writeback continues past
byte-level EOF up to a block-aligned range, or when a concurrent
truncate shrinks the file after end_pos was sampled in
iomap_writeback_handle_eof().

A wrapped io_size can mislead append detection and corrupt
completion-time size handling, since filesystem end_io paths consume
io_size for decisions such as on-disk EOF updates and unwritten/COW
completion ranges.

Fix this by clamping io_size to zero when EOF has moved to or before
the ioend start offset.  This preserves the original intent of trimming
io_size to valid in-EOF data while avoiding the underflow.

## References
- https://git.kernel.org/stable/c/1f38f65bf965fce9aa159d45c5347538f56c5973
- https://git.kernel.org/stable/c/55ec50d046c03b3724741957f7b007856e36dbe7
- https://git.kernel.org/stable/c/7f7780abb4c0fdc9a2603aea8e985ff14ee900e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

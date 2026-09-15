# [H] io_uring/rsrc: reject zero-length fixed buffer import

## Summary
Severity: High
Advisory: CVE-2026-43006
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43006
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/rsrc: reject zero-length fixed buffer import

validate_fixed_range() admits buf_addr at the exact end of the
registered region when len is zero, because the check uses strict
greater-than (buf_end > imu->ubuf + imu->len).  io_import_fixed()
then computes offset == imu->len, which causes the bvec skip logic
to advance past the last bio_vec entry and read bv_offset from
out-of-bounds slab memory.

Return early from io_import_fixed() when len is zero.  A zero-length
import has no data to transfer and should not walk the bvec array
at all.

  BUG: KASAN: slab-out-of-bounds in io_import_reg_buf+0x697/0x7f0
  Read of size 4 at addr ffff888002bcc254 by task poc/103
  Call Trace:
   io_import_reg_buf+0x697/0x7f0
   io_write_fixed+0xd9/0x250
   __io_issue_sqe+0xad/0x710
   io_issue_sqe+0x7d/0x1100
   io_submit_sqes+0x86a/0x23c0
   __do_sys_io_uring_enter+0xa98/0x1590
  Allocated by task 103:
  The buggy address is located 12 bytes to the right of
   allocated 584-byte region [ffff888002bcc000, ffff888002bcc248)

## References
- https://git.kernel.org/stable/c/040a1e7e0e2f01851fec1dd2d96906f8636a9f75
- https://git.kernel.org/stable/c/111a12b422a8cfa93deabaef26fec48237163214
- https://git.kernel.org/stable/c/40170fc1a79c1b2e68f09ae6aac687b7305ae6f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43006.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

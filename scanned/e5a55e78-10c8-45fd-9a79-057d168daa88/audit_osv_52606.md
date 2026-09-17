# [H] CVE-2021-47636

## Summary
Severity: High
Advisory: CVE-2021-47636
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47636
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix read out-of-bounds in ubifs_wbuf_write_nolock()

Function ubifs_wbuf_write_nolock() may access buf out of bounds in
following process:

ubifs_wbuf_write_nolock():
  aligned_len = ALIGN(len, 8);   // Assume len = 4089, aligned_len = 4096
  if (aligned_len <= wbuf->avail) ... // Not satisfy
  if (wbuf->used) {
    ubifs_leb_write()  // Fill some data in avail wbuf
    len -= wbuf->avail;   // len is still not 8-bytes aligned
    aligned_len -= wbuf->avail;
  }
  n = aligned_len >> c->max_write_shift;
  if (n) {
    n <<= c->max_write_shift;
    err = ubifs_leb_write(c, wbuf->lnum, buf + written,
                          wbuf->offs, n);
    // n > len, read out of bounds less than 8(n-len) bytes
  }

, which can be catched by KASAN:
  =========================================================
  BUG: KASAN: slab-out-of-bounds in ecc_sw_hamming_calculate+0x1dc/0x7d0
  Read of size 4 at addr ffff888105594ff8 by task kworker/u8:4/128
  Workqueue: writeback wb_workfn (flush-ubifs_0_0)
  Call Trace:
    kasan_report.cold+0x81/0x165
    nand_write_page_swecc+0xa9/0x160
    ubifs_leb_write+0xf2/0x1b0 [ubifs]
    ubifs_wbuf_write_nolock+0x421/0x12c0 [ubifs]
    write_head+0xdc/0x1c0 [ubifs]
    ubifs_jnl_write_inode+0x627/0x960 [ubifs]
    wb_workfn+0x8af/0xb80

Function ubifs_wbuf_write_nolock() accepts that parameter 'len' is not 8
bytes aligned, the 'len' represents the true length of buf (which is
allocated in 'ubifs_jnl_xxx', eg. ubifs_jnl_write_inode), so
ubifs_wbuf_write_nolock() must handle the length read from 'buf' carefully
to write leb safely.

Fetch a reproducer in [Link].

## References
- https://git.kernel.org/stable/c/4f2262a334641e05f645364d5ade1f565c85f20b
- https://git.kernel.org/stable/c/5343575aa11c5d7044107d59d43f84aec01312b0
- https://git.kernel.org/stable/c/a7054aaf1909cf40489c0ec1b728fdcf79c751a6
- https://git.kernel.org/stable/c/b80ccbec0e4804436c382d7dd60e943c386ed83a
- https://git.kernel.org/stable/c/e09fa5318d51f522e1af4fbaf8f74999355980c8
- https://git.kernel.org/stable/c/07a209fadee7b53b46858538e1177597273862e4
- https://git.kernel.org/stable/c/3b7fb89135a20587d57f8877c02e25003e9edbdf

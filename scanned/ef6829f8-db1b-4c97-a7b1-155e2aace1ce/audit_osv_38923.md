# [H] ocfs2: validate inline data i_size during inode read

## Summary
Severity: High
Advisory: CVE-2026-43076
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43076
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: validate inline data i_size during inode read

When reading an inode from disk, ocfs2_validate_inode_block() performs
various sanity checks but does not validate the size of inline data.  If
the filesystem is corrupted, an inode's i_size can exceed the actual
inline data capacity (id_count).

This causes ocfs2_dir_foreach_blk_id() to iterate beyond the inline data
buffer, triggering a use-after-free when accessing directory entries from
freed memory.

In the syzbot report:
  - i_size was 1099511627576 bytes (~1TB)
  - Actual inline data capacity (id_count) is typically <256 bytes
  - A garbage rec_len (54648) caused ctx->pos to jump out of bounds
  - This triggered a UAF in ocfs2_check_dir_entry()

Fix by adding a validation check in ocfs2_validate_inode_block() to ensure
inodes with inline data have i_size <= id_count.  This catches the
corruption early during inode read and prevents all downstream code from
operating on invalid data.

## References
- https://git.kernel.org/stable/c/131c0b573e1b467b7d553e9ff38003f1acd8f5f2
- https://git.kernel.org/stable/c/1524af3685b35feac76662cc551cbc37bd14775f
- https://git.kernel.org/stable/c/37f074e65f24f10f8d8df224a572e4cb9e6faf63
- https://git.kernel.org/stable/c/77d0295725109d77f5854ef5b58c0d06c08168cc
- https://git.kernel.org/stable/c/bcd46bc261b215b3b12c557a978299eafa02ecdd
- https://git.kernel.org/stable/c/c1de19e891be3bfb3e1d0c7cf07bbb8fb3b77c1b
- https://git.kernel.org/stable/c/cd2d765aa7157f852999842af32148128c735d39
- https://git.kernel.org/stable/c/d012c782abcabe68b5b9e71be58a15e9f9d83dc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

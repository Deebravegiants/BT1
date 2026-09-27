# [H] fs/ntfs3: add bounds check to run_get_highest_vcn()

## Summary
Severity: High
Advisory: CVE-2026-72478
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72478
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: add bounds check to run_get_highest_vcn()

run_get_highest_vcn() parses a packed NTFS mapping-pairs buffer without
any length bound, relying solely on a 0x00 terminator to stop.  A
crafted $LogFile UpdateMappingPairs record whose embedded attribute
contains mapping-pairs runs without a terminator causes the function to
read past the slab allocation, triggering a KASAN slab-out-of-bounds
read on mount.

The sibling function run_unpack() received an analogous bounds-check in
commit b62567bca474 ("ntfs3: add buffer boundary checks to run_unpack()"),
but run_get_highest_vcn() was missed.

Take a run_buf_size parameter and reject any run header whose payload
would extend past the buffer end, mirroring the pattern used by
run_unpack().  The caller in fslog.c passes the remaining attribute
bytes after the mapping-pairs offset.

KASAN report (on mainline v7.1 merge window HEAD):

  BUG: KASAN: slab-out-of-bounds in run_get_highest_vcn+0x3c0/0x410
  Read of size 1 at addr ffff88800e2d5400 by task mount/72
  Call Trace:
   run_get_highest_vcn+0x3c0/0x410
   do_action.isra.0+0x3ba8/0x7b50
   log_replay+0x9ddd/0x10200
   ntfs_loadlog_and_replay+0x4ad/0x610
   ntfs_fill_super+0x214a/0x4540

## References
- https://git.kernel.org/stable/c/41081202eb823f5b27ff164b12010b24428100ad
- https://git.kernel.org/stable/c/8afc24a884aff6a6f08028bd779ee65c40054455
- https://git.kernel.org/stable/c/a31893206588374d7d16fad387189d8165c7efd3
- https://git.kernel.org/stable/c/bb11485a87fbb2254b62cfed630b699d50e57da8
- https://git.kernel.org/stable/c/c23083b472a720c3f60b147db05b25b751c7c1bf
- https://git.kernel.org/stable/c/c69b9003332917b652175d5fa9d84158c5ed8617
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72478.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

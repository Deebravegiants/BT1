# [H] iomap: Fix possible overflow condition in iomap_write_delalloc_scan

## Summary
Severity: High
Advisory: CVE-2023-54285
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54285
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.162, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: Fix possible overflow condition in iomap_write_delalloc_scan

folio_next_index() returns an unsigned long value which left shifted
by PAGE_SHIFT could possibly cause an overflow on 32-bit system. Instead
use folio_pos(folio) + folio_size(folio), which does this correctly.

## References
- https://git.kernel.org/stable/c/0c6cf409093f307ee05114f834516730c0da5b21
- https://git.kernel.org/stable/c/5c281b0c5d18c8eeb1cfd5023f4adb153e6d1240
- https://git.kernel.org/stable/c/eee2d2e6ea5550118170dbd5bb1316ceb38455fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54285.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

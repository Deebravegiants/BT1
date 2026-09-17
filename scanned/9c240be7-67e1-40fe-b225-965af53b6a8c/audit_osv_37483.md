# [H] fuse: reject oversized dirents in page cache

## Summary
Severity: High
Advisory: CVE-2026-31694
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31694
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: reject oversized dirents in page cache

fuse_add_dirent_to_cache() computes a serialized dirent size from the
server-controlled namelen field and copies the dirent into a single
page-cache page. The existing logic only checks whether the dirent fits
in the remaining space of the current page and advances to a fresh page
if not. It never checks whether the dirent itself exceeds PAGE_SIZE.

As a result, a malicious FUSE server can return a dirent with
namelen=4095, producing a serialized record size of 4120 bytes. On 4 KiB
page systems this causes memcpy() to overflow the cache page by 24 bytes
into the following kernel page.

Reject dirents that cannot fit in a single page before copying them into
the readdir cache.

## References
- https://git.kernel.org/stable/c/474ce83c96a55f2eeb14dee2be375eeadfdacdf5
- https://git.kernel.org/stable/c/51a8de6c50bf947c8f534cd73da4c8f0a13e7bed
- https://git.kernel.org/stable/c/7de93abfaae1b2dc94da8a07a36421bd073f1d8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31694.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

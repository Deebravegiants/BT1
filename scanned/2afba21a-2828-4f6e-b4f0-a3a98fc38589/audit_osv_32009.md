# [H] md/md-bitmap: fix wrong bitmap_limit for clustermd when write sb

## Summary
Severity: High
Advisory: CVE-2025-22124
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22124
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.46, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/md-bitmap: fix wrong bitmap_limit for clustermd when write sb

In clustermd, separate write-intent-bitmaps are used for each cluster
node:

0                    4k                     8k                    12k
-------------------------------------------------------------------
| idle                | md super            | bm super [0] + bits |
| bm bits[0, contd]   | bm super[1] + bits  | bm bits[1, contd]   |
| bm super[2] + bits  | bm bits [2, contd]  | bm super[3] + bits  |
| bm bits [3, contd]  |                     |                     |

So in node 1, pg_index in __write_sb_page() could equal to
bitmap->storage.file_pages. Then bitmap_limit will be calculated to
0. md_super_write() will be called with 0 size.
That means the first 4k sb area of node 1 will never be updated
through filemap_write_page().
This bug causes hang of mdadm/clustermd_tests/01r1_Grow_resize.

Here use (pg_index % bitmap->storage.file_pages) to make calculation
of bitmap_limit correct.

## References
- https://git.kernel.org/stable/c/60196f92bbc7901eb5cfa5d456651b87ea50a4a3
- https://git.kernel.org/stable/c/6130825f34d41718c98a9b1504a79a23e379701e
- https://git.kernel.org/stable/c/bc3a9788961631359527763d7e1fcf26554c7cb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22124.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] fs/ntfs3: Initialize new folios before use

## Summary
Severity: High
Advisory: CVE-2025-71311
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2025-71311
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Initialize new folios before use

KMSAN reports an uninitialized value in longest_match_std(), invoked
from ntfs_compress_write(). When new folios are allocated without being
marked uptodate and ni_read_frame() is skipped because the caller expects
the frame to be completely overwritten, some reserved folios may remain
only partially filled, leaving the rest memory uninitialized.

## References
- https://git.kernel.org/stable/c/41d79f8e2a36622d148719bf7c18b46ac1264284
- https://git.kernel.org/stable/c/5a30cc03bde169ad558695b26da6ea7e55f6194a
- https://git.kernel.org/stable/c/dd6c81527d097b3b0bf5a15c2fdc9657d045144c
- https://git.kernel.org/stable/c/f223ebffa185cc8da934333c5a31ff2d4f992dc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71311.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

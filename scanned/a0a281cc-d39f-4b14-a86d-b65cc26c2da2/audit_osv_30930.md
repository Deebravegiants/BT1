# [M] erofs: fix blksize < PAGE_SIZE for file-backed mounts

## Summary
Severity: Medium
Advisory: CVE-2024-56750
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56750
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix blksize < PAGE_SIZE for file-backed mounts

Adjust sb->s_blocksize{,_bits} directly for file-backed
mounts when the fs block size is smaller than PAGE_SIZE.

Previously, EROFS used sb_set_blocksize(), which caused
a panic if bdev-backed mounts is not used.

## References
- https://git.kernel.org/stable/c/679d8537e5748241c71ac97a6b6dc919eae31716
- https://git.kernel.org/stable/c/bae0854160939a64a092516ff1b2f221402b843b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56750.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

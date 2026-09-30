# [M] erofs: fix inconsistent per-file compression format

## Summary
Severity: Medium
Advisory: CVE-2024-26590
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-26590
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.80, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix inconsistent per-file compression format

EROFS can select compression algorithms on a per-file basis, and each
per-file compression algorithm needs to be marked in the on-disk
superblock for initialization.

However, syzkaller can generate inconsistent crafted images that use
an unsupported algorithmtype for specific inodes, e.g. use MicroLZMA
algorithmtype even it's not set in `sbi->available_compr_algs`.  This
can lead to an unexpected "BUG: kernel NULL pointer dereference" if
the corresponding decompressor isn't built-in.

Fix this by checking against `sbi->available_compr_algs` for each
m_algorithmformat request.  Incorrect !erofs_sb_has_compr_cfgs preset
bitmap is now fixed together since it was harmless previously.

## References
- https://git.kernel.org/stable/c/118a8cf504d7dfa519562d000f423ee3ca75d2c4
- https://git.kernel.org/stable/c/47467e04816cb297905c0f09bc2d11ef865942d9
- https://git.kernel.org/stable/c/823ba1d2106019ddf195287ba53057aee33cf724
- https://git.kernel.org/stable/c/eed24b816e50c6cd18cbee0ff0d7218c8fced199
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26590.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

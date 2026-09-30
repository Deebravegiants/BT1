# [H] erofs: fix buffer copy overflow of ztailpacking feature

## Summary
Severity: High
Advisory: CVE-2022-49464
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49464
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix buffer copy overflow of ztailpacking feature

I got some KASAN report as below:

[   46.959738] ==================================================================
[   46.960430] BUG: KASAN: use-after-free in z_erofs_shifted_transform+0x2bd/0x370
[   46.960430] Read of size 4074 at addr ffff8880300c2f8e by task fssum/188
...
[   46.960430] Call Trace:
[   46.960430]  <TASK>
[   46.960430]  dump_stack_lvl+0x41/0x5e
[   46.960430]  print_report.cold+0xb2/0x6b7
[   46.960430]  ? z_erofs_shifted_transform+0x2bd/0x370
[   46.960430]  kasan_report+0x8a/0x140
[   46.960430]  ? z_erofs_shifted_transform+0x2bd/0x370
[   46.960430]  kasan_check_range+0x14d/0x1d0
[   46.960430]  memcpy+0x20/0x60
[   46.960430]  z_erofs_shifted_transform+0x2bd/0x370
[   46.960430]  z_erofs_decompress_pcluster+0xaae/0x1080

The root cause is that the tail pcluster won't be a complete filesystem
block anymore. So if ztailpacking is used, the second part of an
uncompressed tail pcluster may not be ``rq->pageofs_out``.

## References
- https://git.kernel.org/stable/c/4d53a625f29074e7b8236c2c0e0922edb7608df9
- https://git.kernel.org/stable/c/6b59e1907f58cf877c563dcf013159eb9f994b64
- https://git.kernel.org/stable/c/dcbe6803fffd387f72b48c2373b5f5ed12a5804b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49464.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49464
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

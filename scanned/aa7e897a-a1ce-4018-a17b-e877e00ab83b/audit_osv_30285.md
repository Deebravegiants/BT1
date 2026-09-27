# [H] dm cache: fix out-of-bounds access to the dirty bitset when resizing

## Summary
Severity: High
Advisory: CVE-2024-50279
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50279
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm cache: fix out-of-bounds access to the dirty bitset when resizing

dm-cache checks the dirty bits of the cache blocks to be dropped when
shrinking the fast device, but an index bug in bitset iteration causes
out-of-bounds access.

Reproduce steps:

1. create a cache device of 1024 cache blocks (128 bytes dirty bitset)

dmsetup create cmeta --table "0 8192 linear /dev/sdc 0"
dmsetup create cdata --table "0 131072 linear /dev/sdc 8192"
dmsetup create corig --table "0 524288 linear /dev/sdc 262144"
dd if=/dev/zero of=/dev/mapper/cmeta bs=4k count=1 oflag=direct
dmsetup create cache --table "0 524288 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 writethrough smq 0"

2. shrink the fast device to 512 cache blocks, triggering out-of-bounds
   access to the dirty bitset (offset 0x80)

dmsetup suspend cache
dmsetup reload cdata --table "0 65536 linear /dev/sdc 8192"
dmsetup resume cdata
dmsetup resume cache

KASAN reports:

  BUG: KASAN: vmalloc-out-of-bounds in cache_preresume+0x269/0x7b0
  Read of size 8 at addr ffffc900000f3080 by task dmsetup/131

  (...snip...)
  The buggy address belongs to the virtual mapping at
   [ffffc900000f3000, ffffc900000f5000) created by:
   cache_ctr+0x176a/0x35f0

  (...snip...)
  Memory state around the buggy address:
   ffffc900000f2f80: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
   ffffc900000f3000: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  >ffffc900000f3080: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
                     ^
   ffffc900000f3100: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
   ffffc900000f3180: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8

Fix by making the index post-incremented.

## References
- https://git.kernel.org/stable/c/3b02c40ff10fdf83cc545850db208de855ebe22c
- https://git.kernel.org/stable/c/4fa4feb873cea0e9d6ff883b37cca6f33169d8b4
- https://git.kernel.org/stable/c/56507203e1b6127967ec2b51fb0b23a0d4af1334
- https://git.kernel.org/stable/c/792227719725497ce10a8039803bec13f89f8910
- https://git.kernel.org/stable/c/8501e38dc9e0060814c4085815fc83da3e6d43bf
- https://git.kernel.org/stable/c/e57648ce325fa405fe6bbd0e6a618ced7c301a2d
- https://git.kernel.org/stable/c/ee1f74925717ab36f6a091104c170639501ce818
- https://git.kernel.org/stable/c/ff1dd8a04c30e8d4e2fd5c83198ca672eb6a9e7f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50279.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

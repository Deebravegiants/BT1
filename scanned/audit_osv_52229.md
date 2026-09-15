# [M] CVE-2021-47221

## Summary
Severity: Medium
Advisory: CVE-2021-47221
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47221
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/slub: actually fix freelist pointer vs redzoning

It turns out that SLUB redzoning ("slub_debug=Z") checks from
s->object_size rather than from s->inuse (which is normally bumped to
make room for the freelist pointer), so a cache created with an object
size less than 24 would have the freelist pointer written beyond
s->object_size, causing the redzone to be corrupted by the freelist
pointer.  This was very visible with "slub_debug=ZF":

  BUG test (Tainted: G    B            ): Right Redzone overwritten
  -----------------------------------------------------------------------------

  INFO: 0xffff957ead1c05de-0xffff957ead1c05df @offset=1502. First byte 0x1a instead of 0xbb
  INFO: Slab 0xffffef3950b47000 objects=170 used=170 fp=0x0000000000000000 flags=0x8000000000000200
  INFO: Object 0xffff957ead1c05d8 @offset=1496 fp=0xffff957ead1c0620

  Redzone  (____ptrval____): bb bb bb bb bb bb bb bb               ........
  Object   (____ptrval____): 00 00 00 00 00 f6 f4 a5               ........
  Redzone  (____ptrval____): 40 1d e8 1a aa                        @....
  Padding  (____ptrval____): 00 00 00 00 00 00 00 00               ........

Adjust the offset to stay within s->object_size.

(Note that no caches of in this size range are known to exist in the
kernel currently.)

## References
- https://git.kernel.org/stable/c/ce6e8bee7a3883e8008b30f5887dbb426aac6a35
- https://git.kernel.org/stable/c/e41a49fadbc80b60b48d3c095d9e2ee7ef7c9a8e
- https://git.kernel.org/stable/c/f6ed2357541612a13a5841b3af4dc32ed984a25f

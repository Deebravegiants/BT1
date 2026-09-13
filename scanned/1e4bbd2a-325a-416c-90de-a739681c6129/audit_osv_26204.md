# [H] erofs: fix lz4 inplace decompression

## Summary
Severity: High
Advisory: CVE-2023-52497
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52497
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.285, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix lz4 inplace decompression

Currently EROFS can map another compressed buffer for inplace
decompression, that was used to handle the cases that some pages of
compressed data are actually not in-place I/O.

However, like most simple LZ77 algorithms, LZ4 expects the compressed
data is arranged at the end of the decompressed buffer and it
explicitly uses memmove() to handle overlapping:
  __________________________________________________________
 |_ direction of decompression --> ____ |_ compressed data _|

Although EROFS arranges compressed data like this, it typically maps two
individual virtual buffers so the relative order is uncertain.
Previously, it was hardly observed since LZ4 only uses memmove() for
short overlapped literals and x86/arm64 memmove implementations seem to
completely cover it up and they don't have this issue.  Juhyung reported
that EROFS data corruption can be found on a new Intel x86 processor.
After some analysis, it seems that recent x86 processors with the new
FSRM feature expose this issue with "rep movsb".

Let's strictly use the decompressed buffer for lz4 inplace
decompression for now.  Later, as an useful improvement, we could try
to tie up these two buffers together in the correct order.

## References
- https://git.kernel.org/stable/c/33bf23c9940dbd3a22aad7f0cda4c84ed5701847
- https://git.kernel.org/stable/c/3c12466b6b7bf1e56f9b32c366a3d83d87afb4de
- https://git.kernel.org/stable/c/77cbc04a1a8610e303a0e0d74f2676667876a184
- https://git.kernel.org/stable/c/9ff2d260b25df6fe1341a79113d88fecf6bd553e
- https://git.kernel.org/stable/c/a0180e940cf1aefa7d516e20b259ad34f7a8b379
- https://git.kernel.org/stable/c/bffc4cc334c5bb31ded54bc3cfd651735a3cb79e
- https://git.kernel.org/stable/c/f36d200a80a3ca025532ed60dd1ac21b620e14ae
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52497.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52497
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

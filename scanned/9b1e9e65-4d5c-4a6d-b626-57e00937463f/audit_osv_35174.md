# [C] iomap: adjust read range correctly for non-block-aligned positions

## Summary
Severity: Critical
Advisory: CVE-2025-68794
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68794
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: adjust read range correctly for non-block-aligned positions

iomap_adjust_read_range() assumes that the position and length passed in
are block-aligned. This is not always the case however, as shown in the
syzbot generated case for erofs. This causes too many bytes to be
skipped for uptodate blocks, which results in returning the incorrect
position and length to read in. If all the blocks are uptodate, this
underflows length and returns a position beyond the folio.

Fix the calculation to also take into account the block offset when
calculating how many bytes can be skipped for uptodate blocks.

## References
- https://git.kernel.org/stable/c/12053695c8ef5410e8cc6c9ed4c0db9cd9c82b3e
- https://git.kernel.org/stable/c/142194fb21afe964d2d194cab1fc357cbf87e899
- https://git.kernel.org/stable/c/275b37a1e5c2c8abd313e8075f6aec9a349f291b
- https://git.kernel.org/stable/c/7aa6bc3e8766990824f66ca76c19596ce10daf3e
- https://git.kernel.org/stable/c/82b60ffbb532d919959702768dca04c3c0500ae5
- https://git.kernel.org/stable/c/b8c9f25fd84328c5fcc4f70c6d1e8f1d4787eaac
- https://git.kernel.org/stable/c/ce20f49ac9194cf81a77f01d1c316d7c17ae753c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68794.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68794
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

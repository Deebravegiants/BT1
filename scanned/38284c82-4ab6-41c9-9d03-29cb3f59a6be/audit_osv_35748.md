# [H] Imager versions before 1.032 for Perl have a heap out-of-bounds read in the bundled Imager::File::SGI reader via a 16-bit RLE literal run in read_rgb_16_rle

## Summary
Severity: High
Advisory: CVE-2026-13705
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-13705
Type: osv

## Details
Imager versions before 1.032 for Perl have a heap out-of-bounds read in the bundled Imager::File::SGI reader via a 16-bit RLE literal run in read_rgb_16_rle.

read_rgb_16_rle guards each literal run with if (count > data_left), but count is a pixel count while every 16-bit sample consumes two bytes. The copy loop reads inp[0] * 256 + inp[1] and advances two bytes per pixel, so a run with data_left / 2 < count <= data_left passes the guard yet consumes 2 * count bytes and reads past the end of the buffer. The 8-bit path is unaffected because there one pixel is one byte.

Reading a crafted SGI image through Imager->read triggers the over-read before the parser rejects the malformed image, which can crash the process.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13705.json
- https://metacpan.org/release/TONYC/Imager-1.032/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13705
- https://github.com/tonycoz/imager/commit/f28de02770dfc26ffbdc32048970ed84babbf730.patch
- https://github.com/tonycoz/imager

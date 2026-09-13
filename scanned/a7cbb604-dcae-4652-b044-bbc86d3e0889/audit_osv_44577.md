# [M] Imager::File::GIF versions through 1.002 for Perl allow a heap out of bounds (OOB) write on crafted multi-frame GIF files

## Summary
Severity: Medium
Advisory: CVE-2026-8454
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8454
Type: osv

## Details
Imager::File::GIF versions through 1.002 for Perl allow a heap out of bounds (OOB) write on crafted multi-frame GIF files.

Imager::File::GIF's i_readgif_multi_low allocates a single per-row buffer GifRow sized for the GIF's global screen width 'SWidth' and reuses it across every image in the file.

The page-match branch validates Image.Width + Image.Left > SWidth before each DGifGetLine write, but the parallel skip-image branch at imgif.c:790-805 calls DGifGetLine(GifFile, GifRow, Width) with no such check.

## References
- http://www.openwall.com/lists/oss-security/2026/05/15/15
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8454.json
- https://metacpan.org/release/TONYC/Imager-File-GIF-1.003/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8454
- https://github.com/tonycoz/imager/commit/782e9c06cc75a0f7eed383f39522f51f44598b04.patch
- https://github.com/tonycoz/imager

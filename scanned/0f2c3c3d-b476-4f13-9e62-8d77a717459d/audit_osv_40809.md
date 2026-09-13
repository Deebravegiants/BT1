# [M] SumatraPDF: Heap out-of-bounds write in vendored CHMLib LZX Huffman table construction reachable from crafted CHM files

## Summary
Severity: Medium
Advisory: CVE-2026-55586
Aliases: GHSA-m423-rp8p-whj8
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55586
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. In 3.6.1 and earlier, a crafted CHM file can supply malformed LZX Huffman code lengths to make_decode_table in ext/CHMLib/lzx.c. In the long-code branch, the function writes new internal nodes through next_symbol before validating that the canonical Huffman table has overflowed. The PRETREE case can write beyond the 104-entry PRETREE_table into adjacent heap state in struct LZXstate when reached through chm_open, chm_retrieve_object, LZXdecompress, and BUILD_TABLE. This produces heap memory corruption in the parser process, while arbitrary code execution has not been demonstrated. No fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55586.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-m423-rp8p-whj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-55586
- https://github.com/sumatrapdfreader/sumatrapdf/commit/13b3d4204dd12d93d426f2157b157b149edc29bf

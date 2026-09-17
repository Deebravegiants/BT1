# [M] SumatraPDF has a heap out-of-bounds read in MOBI HuffDic decompressor

## Summary
Severity: Medium
Advisory: CVE-2026-25920
Aliases: GHSA-5mwx-65x7-cffp
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25920
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. In 3.5.2 and earlier, a heap out-of-bounds read vulnerability exists in SumatraPDF's MOBI HuffDic decompressor. The bounds check in AddCdicData() only validates half the range that DecodeOne() actually accesses. Opening a crafted .mobi file can read nearly (1 << codeLength) bytes beyond the CDIC dictionary buffer, leading to a crash.

## References
- https://github.com/sumatrapdfreader/sumatrapdf/blob/916392f94bc34e24f3c3286893ac6d7fa1e1c428/src/MobiDoc.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25920.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-5mwx-65x7-cffp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25920
- https://github.com/sumatrapdfreader/sumatrapdf/commit/12b6887e9dfff874fe8749bab1bdc53d4ff075b3

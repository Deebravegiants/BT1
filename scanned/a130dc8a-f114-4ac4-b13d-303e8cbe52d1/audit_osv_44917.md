# [C] Tesseract: Heap out-of-bounds write in GenericVector<T>::read due to independent reserved/size_used_ fields

## Summary
Severity: Critical
Advisory: CVE-2026-88051
Aliases: GHSA-88qp-4g94-3rf3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88051
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, the callback form of GenericVector::read in src/ccutil/genericvector.h reads the independent int32 fields reserved and size_used_ from a .traineddata model without a cap or an invariant check. reserve(reserved) allocates the backing array, but the callback loop writes size_used_ elements. A crafted TESSDATA_INTTEMP component with version_id 4 or later can therefore set reserved to a small value and size_used_ to a large value when fontinfo_table_.read(fp, read_info) is called from src/classify/intproto.cpp, causing a heap out-of-bounds write of FontInfo structures, heap corruption, a crash, or potentially controlled corruption. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88051.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-88qp-4g94-3rf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-88051
- https://github.com/tesseract-ocr/tesseract/commit/56e09ca12e751623fe796ce1554ce704bffd2ef0

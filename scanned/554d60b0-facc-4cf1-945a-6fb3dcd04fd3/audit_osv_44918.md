# [H] Tesseract: Heap out-of-bounds write in UNICHARSET::load_via_fgets via count/insert desynchronization

## Summary
Severity: High
Advisory: CVE-2026-88052
Aliases: GHSA-2hm8-q5c7-c373
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88052
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, UNICHARSET::load_via_fgets in src/ccutil/unicharset.cpp trusts the declared unichar count as a loop bound and uses id as an unchecked index into the unichars vector. unichar_insert_backwards_compatible can leave the vector unchanged for an empty, duplicate, or already-encodable representation, causing id to become larger than unichars.size(). Subsequent set_* calls and the write to unichars[id].properties.enabled then write UNICHAR_PROPERTIES beyond the vector during initialization in both the default LSTM and legacy engines, causing heap corruption, a crash, or potentially controlled corruption. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88052.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-2hm8-q5c7-c373
- https://nvd.nist.gov/vuln/detail/CVE-2026-88052
- https://github.com/tesseract-ocr/tesseract/commit/2d04d640db2e8c7e3bab2369d599343b5a8b8443

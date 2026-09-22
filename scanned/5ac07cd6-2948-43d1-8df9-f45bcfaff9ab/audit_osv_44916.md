# [M] Tesseract: Out-of-bounds write in UnicharCompress via unvalidated recoder code values

## Summary
Severity: Medium
Advisory: CVE-2026-88050
Aliases: GHSA-7v9h-3q3m-w68g
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88050
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, RecodedCharID::DeSerialize in src/ccutil/unicharcompress.h validates length_ but accepts negative code_ values from a crafted .traineddata recoder component. UnicharCompress::ComputeCodeRange in src/ccutil/unicharcompress.cpp can consequently produce code_range_ equal to zero, after which SetupDecoder indexes is_valid_start_ with the negative code on a size-zero vector. The resulting out-of-bounds bit write uses a large wrapped index and reliably causes a wild-address crash or allocation failure on the default LSTM engine. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88050.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-7v9h-3q3m-w68g
- https://nvd.nist.gov/vuln/detail/CVE-2026-88050
- https://github.com/tesseract-ocr/tesseract/commit/c94a5532ee04db5a4919542832fd94caee5ea58f

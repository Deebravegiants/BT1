# [H] Tesseract: Heap out-of-bounds write in LSTM Convolve layer via crafted .traineddata

## Summary
Severity: High
Advisory: CVE-2026-73066
Aliases: GHSA-7j76-5rq5-5jg8
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73066
Type: osv

## Details
Tesseract is an open source OCR engine. Prior to 5.5.3, a crafted .traineddata LSTM model component loaded through Tesseract's deserializer can cause an unchecked signed integer multiplication in Convolve::DeSerialize in src/lstm/convolve.cpp to wrap the convolution output-channel count, undersizing the forward-pass output buffer while writes use the unwrapped element count and causing a heap out-of-bounds write during OCR recognition. This issue is fixed in version 5.5.3.

## References
- https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73066.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-7j76-5rq5-5jg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73066
- https://github.com/tesseract-ocr/tesseract/commit/2f4d2f4bf45c363785d7bf1da29b6628f8939a72
- https://github.com/tesseract-ocr/tesseract/pull/4588

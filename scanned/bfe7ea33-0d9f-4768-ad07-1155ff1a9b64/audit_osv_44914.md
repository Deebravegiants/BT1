# [C] Tesseract: Heap out-of-bounds write/read in FullyConnected::Forward via layer/weight-matrix dimension mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-88048
Aliases: GHSA-q44c-23p6-5mw6
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88048
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, FullyConnected::DeSerialize in src/lstm/fullyconnected.cpp does not validate the deserialized layer scalars ni_ and no_ against the weight-matrix dimensions. During FullyConnected::Forward, MatrixDotVector in src/lstm/weightmatrix.cpp writes w.dim1() results into temp_line, which is sized from no_, and reads w.dim2() minus one inputs from curr_input, which is sized from ni_. A crafted .traineddata NT_SOFTMAX layer can therefore use inconsistent dimensions to cause a heap out-of-bounds write and read on the default LSTM engine, resulting in heap corruption, a crash, information disclosure, or potentially controlled corruption. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88048.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-q44c-23p6-5mw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-88048
- https://github.com/tesseract-ocr/tesseract/commit/103dc134eb36411ddc6833ec20aa2c76795bd0ff

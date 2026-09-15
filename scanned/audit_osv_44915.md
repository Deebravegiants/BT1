# [C] Tesseract: Heap out-of-bounds write in LSTM::Forward via na_/gate-matrix dimension mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-88049
Aliases: GHSA-jgq8-pprg-vc68
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88049
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, prior .traineddata hardening added bounds checks to NetworkIO::CopyTimeStepGeneral and NetworkIO::Randomize in src/lstm/networkio.cpp but left NetworkIO::WriteTimeStepPart and NetworkIO::AddTimeStepPart unchecked. In LSTM::Forward in src/lstm/lstm.cpp, source_ is sized from the independently deserialized na_ field while the WriteTimeStepPart count is ns_, which comes from the CI gate WeightMatrix dim1() value. A crafted NT_LSTM layer can make ns_ much larger than na_, causing a heap out-of-bounds write during the first recognition step on the default LSTM engine and resulting in heap corruption, a crash, or potentially controlled corruption. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88049.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-jgq8-pprg-vc68
- https://nvd.nist.gov/vuln/detail/CVE-2026-88049
- https://github.com/tesseract-ocr/tesseract/commit/b494ac18925f9d9aff9ef5815475de9943ab19bf

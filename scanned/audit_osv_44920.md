# [M] Tesseract: Denial of service via empty-stack dereference in Plumbing/Series at model load

## Summary
Severity: Medium
Advisory: CVE-2026-88054
Aliases: GHSA-f6h7-cqr4-6fx4
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88054
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, Plumbing::DeSerialize in src/lstm/plumbing.cpp rejects excessively large network stacks but accepts a zero-length stack for NT_SERIES, NT_PARALLEL, or NT_REVERSED layers in a crafted .traineddata model. During LSTMRecognizer initialization in src/lstm/lstmrecognizer.cpp, CacheXScaleFactor(XScaleFactor()) reaches Series::CacheXScaleFactor in src/lstm/series.cpp, which dereferences stack_[0] on the empty vector and invokes a virtual method through an invalid Network pointer. This causes a deterministic crash and denial of service at model load. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88054.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-f6h7-cqr4-6fx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-88054
- https://github.com/tesseract-ocr/tesseract/commit/552771236b0d80cbdb0c7dd856120fa21a4672e5

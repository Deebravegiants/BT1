# [C] Tesseract: Heap out-of-bounds write in Classify::ReadIntTemplates via unvalidated counts in crafted .traineddata

## Summary
Severity: Critical
Advisory: CVE-2026-88053
Aliases: GHSA-rphx-x795-5qjv
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88053
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, Classify::ReadIntTemplates in src/classify/intproto.cpp reads NumClassPruners, NumClasses, and NumProtoSets from the TESSDATA_INTTEMP component of a crafted .traineddata file and uses those values as loop bounds without validating them against MAX_NUM_CLASS_PRUNERS, MAX_NUM_CLASSES, and MAX_NUM_PROTO_SETS. The loops store heap pointers into fixed-capacity ClassPruners and ProtoSets arrays in INT_TEMPLATES_STRUCT and INT_CLASS_STRUCT, so an oversized count causes heap out-of-bounds pointer writes during legacy-classifier initialization before OCR begins, resulting in heap corruption, a crash, or potentially controlled corruption. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88053.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-rphx-x795-5qjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-88053
- https://github.com/tesseract-ocr/tesseract/commit/8b0574680f3b22f246ade6a4c8e3029104255c63

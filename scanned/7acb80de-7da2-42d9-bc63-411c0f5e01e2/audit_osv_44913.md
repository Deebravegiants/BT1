# [C] Tesseract: ReadNormProtos stack buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2026-88047
Aliases: GHSA-5j2p-r5vc-q7f3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88047
Type: osv

## Details
Tesseract is an open source OCR engine. In version 5.5.3 and earlier, Classify::ReadNormProtos in src/classify/normmatch.cpp parses the NORMPROTO component of a .traineddata file and uses std::istream::operator>>(char*) to extract a whitespace-delimited token into a fixed 61-byte stack buffer without setting a stream width. The 100-byte line buffer can carry a token of up to 99 characters, so a token longer than 60 characters writes up to 39 attacker-controlled bytes past the buffer during TessBaseAPI::Init of the legacy engine, causing stack corruption, denial of service, and potentially control-flow hijacking on affected standard-library implementations. Builds using Apple's libc++ C++20 bounded array overload are incidentally protected, while typical libstdc++ builds remain affected. No fixed release is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88047.json
- https://github.com/tesseract-ocr/tesseract/security/advisories/GHSA-5j2p-r5vc-q7f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-88047
- https://github.com/tesseract-ocr/tesseract/commit/1bda5079b1c8a7e25f523486837426903d29ce84

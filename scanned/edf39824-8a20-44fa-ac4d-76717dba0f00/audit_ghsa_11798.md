# [C] node-tesseract-ocr is vulnerable to OS Command Injection through unsanitized recognize() function parameter

## Summary
Severity: Critical
Advisory: GHSA-8j44-735h-w4w2
CVE: CVE-2026-26832
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8j44-735h-w4w2
Type: github-advisory

## Affected
- npm: `node-tesseract-ocr` — affected >=0

## Details
node-tesseract-ocr is an npm package that provides a Node.js wrapper for Tesseract OCR. In all versions through 2.2.1, the recognize() function in src/index.js is vulnerable to OS Command Injection. The file path parameter is concatenated into a shell command string and passed to child_process.exec() without proper sanitization

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26832
- https://github.com/zapolnoch/node-tesseract-ocr
- https://github.com/zapolnoch/node-tesseract-ocr/blob/master/src/index.js
- https://github.com/zebbernCVE/CVE-2026-26832

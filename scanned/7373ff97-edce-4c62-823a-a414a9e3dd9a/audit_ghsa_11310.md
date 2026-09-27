# [C] textract is vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-9pcj-m5rr-p28g
CVE: CVE-2026-26831
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-9pcj-m5rr-p28g
Type: github-advisory

## Affected
- npm: `textract` — affected >=0

## Details
textract through 2.5.0 is vulnerable to OS Command Injection via the file path parameter in multiple extractors. When processing files with malicious filenames, the filePath is passed directly to child_process.exec() in lib/extractors/doc.js, rtf.js, dxf.js, images.js, and lib/util.js with inadequate sanitization

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26831
- https://github.com/dbashford/textract
- https://github.com/dbashford/textract/blob/master/lib/extractors/doc.js
- https://github.com/dbashford/textract/blob/master/lib/extractors/rtf.js
- https://github.com/dbashford/textract/blob/master/lib/util.js
- https://github.com/zebbernCVE/CVE-2026-26831
- https://www.npmjs.com/package/textract

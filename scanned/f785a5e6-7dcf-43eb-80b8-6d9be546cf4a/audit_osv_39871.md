# [C] Streambert: Arbitrary File Write (Zip Slip) via Subtitle Extraction

## Summary
Severity: Critical
Advisory: CVE-2026-48055
Aliases: GHSA-3q2x-3q9p-qwfc
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48055
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download any video media. In versions 2.4.0 and prior, a high-severity Zip Slip vulnerability was identified in Streambert's subtitle extraction logic. The application does not sanitize archive entry filenames during extraction, allowing a malicious archive to perform path traversal and write arbitrary files to the host filesystem. The subtitle extraction process downloads a ZIP archive and extracts its entries. The destination file path is constructed by concatenating the raw archive entry name (extracted.name) directly to the temporary directory path. If a malicious ZIP archive containing directory traversal sequences is processed, it escapes the temporary directory boundaries. The application then writes the extracted payload anywhere on the host filesystem subject to the application's current write permissions. This issue has been fixed in version 2.5.0.

## References
- https://github.com/truelockmc/streambert/releases/tag/2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48055.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-3q2x-3q9p-qwfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48055

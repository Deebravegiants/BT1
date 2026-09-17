# [M] surya 0.22.1 Unauthenticated Arbitrary File Read via screenshot server

## Summary
Severity: Medium
Advisory: CVE-2026-85687
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85687
Type: osv

## Details
surya 0.22.1 screenshot server contains an unauthenticated arbitrary file read vulnerability in the /info, /page, and /process routes that accept raw file_path parameters. Attackers can read any image or PDF file on the host by supplying arbitrary file paths to Image.open or pypdfium2.PdfDocument, obtaining rendered contents as base64 and using /info as an existence oracle.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85687.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85687
- https://www.vulncheck.com/advisories/surya-0.22.1-unauthenticated-arbitrary-file-read-via-screenshot-server
- https://github.com/datalab-to/surya/issues/518
- https://github.com/datalab-to/surya
- https://github.com/datalab-to/surya/blob/v0.22.1/surya/scripts/screenshot_app.py

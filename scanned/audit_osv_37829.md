# [M] Stirling-PDF vulnerable to DoS via add-watermark

## Summary
Severity: Medium
Advisory: CVE-2026-33438
Aliases: GHSA-3932-2rfq-87xm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33438
Type: osv

## Details
Stirling-PDF is a locally hosted web application that allows you to perform various operations on PDF files. Versions starting in 2.1.5 and prior to 2.5.2 have Denial of Service (DoS) vulnerability in the Stirling-PDF watermark functionality (`/api/v1/security/add-watermark` endpoint). The vulnerability allows authenticated users to cause resource exhaustion and server crashes by providing extreme values for the `fontSize` and `widthSpacer` parameters. Version 2.5.2 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33438.json
- https://github.com/Stirling-Tools/Stirling-PDF/security/advisories/GHSA-3932-2rfq-87xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33438

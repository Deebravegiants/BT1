# [C] Remote code execution in dawnsparks-node-tesseract

## Summary
Severity: Critical
Advisory: GHSA-88qf-5f3v-pm6m
CVE: CVE-2023-29566
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-88qf-5f3v-pm6m
Type: github-advisory

## Affected
- npm: `dawnsparks-node-tesseract` — affected >=0 <0.4.1

## Details
dawnsparks-node-tesseract before 0.4.1 was discovered to contain a remote code execution (RCE) vulnerability via the child_process function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29566
- https://github.com/rona-dinihari/dawnsparks-node-tesseract/commit/81d1664f0b9fe521534acfae1d5b9c40127b36c1
- https://github.com/omnitaint/Vulnerability-Reports/blob/ec3645003c7f8996459b5b24c722474adc2d599f/reports/dawnsparks-node-tesseract/report.md
- https://github.com/rona-dinihari/dawnsparks-node-tesseract
- https://www.npmjs.com/package/dawnsparks-node-tesseract

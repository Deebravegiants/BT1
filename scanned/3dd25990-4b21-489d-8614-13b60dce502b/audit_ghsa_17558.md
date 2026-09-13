# [M] Erupt Unrestricted Upload of File with Dangerous Type vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5gr5-vmmr-82g6
CVE: CVE-2025-45855
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-5gr5-vmmr-82g6
Type: github-advisory

## Affected
- Maven: `xyz.erupt:erupt` — affected >=0

## Details
An arbitrary file upload vulnerability in the component /upload/GoodsCategory/image of erupt v1.12.19 allows attackers to execute arbitrary code via uploading a crafted file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-45855
- https://gist.github.com/Cafe-Tea/b72d442be434e1dafe7810c938892b06
- https://github.com/erupts/erupt
- https://www.erupt.xyz/#!

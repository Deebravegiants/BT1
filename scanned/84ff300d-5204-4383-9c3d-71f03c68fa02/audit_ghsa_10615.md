# [C] Shopizer has a path traversal issue

## Summary
Severity: Critical
Advisory: GHSA-f5w4-7ccj-5m75
CVE: CVE-2026-36767
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-f5w4-7ccj-5m75
Type: github-advisory

## Affected
- Maven: `com.shopizer:shopizer` — affected >=0

## Details
A path traversal vulnerability in the /content/images/add endpoint of shopizer through version 3.2.5 allows attackers write arbitrary files to any writeable path via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-36767
- https://github.com/shopizer-ecommerce/shopizer/issues/1091
- https://github.com/shopizer-ecommerce/shopizer

# [M] Cross-site scripting in Shopizer

## Summary
Severity: Medium
Advisory: GHSA-378p-hrq3-x4p3
CVE: CVE-2021-33562
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-378p-hrq3-x4p3
Type: github-advisory

## Affected
- Maven: `com.shopizer:shopizer` — affected >=0 <2.17.0

## Details
A reflected cross-site scripting (XSS) vulnerability in Shopizer before 2.17.0 allows remote attackers to inject arbitrary web script or HTML via the ref parameter to a page about an arbitrary product, e.g., a product/insert-product-name-here.html/ref= URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33562
- https://github.com/shopizer-ecommerce/shopizer/commit/197f8c78c8f673b957e41ca2c823afc654c19271
- https://github.com/shopizer-ecommerce/shopizer/compare/2.16.0...2.17.0
- https://www.exploit-db.com/exploits/49901

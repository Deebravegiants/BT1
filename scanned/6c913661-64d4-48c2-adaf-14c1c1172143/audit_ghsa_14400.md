# [C] OpenAPI Generator vulnerable to Server-Side Request Forgery

## Summary
Severity: Critical
Advisory: GHSA-wg4w-5m5r-w3p8
CVE: CVE-2023-27162
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-wg4w-5m5r-w3p8
Type: github-advisory

## Affected
- Maven: `org.openapitools:openapi-generator-project` — affected >=0

## Details
openapi-generator up to v6.4.0 was discovered to contain a Server-Side Request Forgery (SSRF) via the component `/api/gen/clients/{language}`. This vulnerability allows attackers to access network resources and sensitive information via a crafted API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27162
- https://gist.github.com/b33t1e/6121210ebd9efd4f693c73b830d8ab08
- https://github.com/OpenAPITools/openapi-generator
- https://notes.sjtu.edu.cn/s/2_yki_2Xq
- http://openapi-generator.com

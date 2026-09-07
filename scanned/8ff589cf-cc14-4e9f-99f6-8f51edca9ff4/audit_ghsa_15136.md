# [H] Apache ServiceComb Service-Center Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-9xc9-xq7w-vpcr
CVE: CVE-2023-44313
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-9xc9-xq7w-vpcr
Type: github-advisory

## Affected
- Go: `github.com/apache/servicecomb-service-center` — affected >=0 <2.2.0

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache ServiceComb Service-Center. Attackers can obtain sensitive server information through specially crafted requests.This issue affects Apache ServiceComb before 2.1.0 (included). Users are recommended to upgrade to version 2.2.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44313
- https://github.com/apache/servicecomb-service-center
- https://lists.apache.org/thread/kxovd455o9h4f2v811hcov2qknbwld5r
- http://www.openwall.com/lists/oss-security/2024/01/31/4

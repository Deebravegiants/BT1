# [M] Nepxion Discovery vulnerable to potential Information Disclosure due to  Server-Side Request Forgery 

## Summary
Severity: Medium
Advisory: GHSA-hhxh-qphc-v423
CVE: CVE-2022-23464
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-hhxh-qphc-v423
Type: github-advisory

## Affected
- Maven: `com.nepxion:discovery` — affected >=0

## Details
Nepxion Discovery is a solution for Spring Cloud. Discovery is vulnerable to a potential Server-Side Request Forgery (SSRF). RouterResourceImpl uses RestTemplate’s getForEntity to retrieve the contents of a URL containing user-controlled input, potentially resulting in Information Disclosure. There is no patch available for this issue at time of publication. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23464
- https://github.com/Nepxion/Discovery
- https://securitylab.github.com/advisories/GHSL-2022-033_GHSL-2022-034_Discovery

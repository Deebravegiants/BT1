# [H] Denial of Service in Spring Cloud Function

## Summary
Severity: High
Advisory: GHSA-q588-3544-8g33
CVE: CVE-2022-22979
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-22
Source: https://github.com/advisories/GHSA-q588-3544-8g33
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-function-parent` — affected >=0 <3.2.6

## Details
In Spring Cloud Function versions prior to 3.2.6, it is possible for a user who directly interacts with framework provided lookup functionality to cause a denial-of-service condition due to the caching issue in the Function Catalog component of the framework.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22979
- https://github.com/spring-cloud/spring-cloud-function
- https://tanzu.vmware.com/security/cve-2022-22979

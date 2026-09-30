# [M] Request injection in Spring Cloud Gateway

## Summary
Severity: Medium
Advisory: GHSA-2r2v-q399-qq93
CVE: CVE-2021-22051
CWE: CWE-352, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-2r2v-q399-qq93
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-gateway` — affected >=3.0.0 <3.0.5
- Maven: `org.springframework.cloud:spring-cloud-gateway` — affected >=2.2.0 <2.2.10.RELEASE0.5

## Details
Applications using Spring Cloud Gateway are vulnerable to specifically crafted requests that could make an extra request on downstream services. Users of affected versions should apply the following mitigation: 3.0.x users should upgrade to 3.0.5+, 2.2.x users should upgrade to 2.2.10.RELEASE or newer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22051
- https://tanzu.vmware.com/security/cve-2021-22051

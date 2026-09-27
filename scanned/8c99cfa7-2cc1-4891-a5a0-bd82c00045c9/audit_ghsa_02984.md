# [H] Code injection in spring-cloud-netflix-hystrix-dashboard

## Summary
Severity: High
Advisory: GHSA-gx3f-hq7p-8fxv
CVE: CVE-2021-22053
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-gx3f-hq7p-8fxv
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-netflix-hystrix-dashboard` — affected >=0 <2.2.10.RELEASE

## Details
Applications using the `spring-cloud-netflix-hystrix-dashboard` expose a way to execute code submitted within the request URI path during the resolution of view templates. When a request is made at `/hystrix/monitor;[user-provided data]`, the path elements following `hystrix/monitor` are being evaluated as SpringEL expressions, which can lead to code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22053
- https://tanzu.vmware.com/security/cve-2021-22053

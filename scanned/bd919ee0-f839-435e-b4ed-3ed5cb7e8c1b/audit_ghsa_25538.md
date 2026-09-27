# [C] Spring Cloud Function Code Injection with a specially crafted SpEL as a routing expression

## Summary
Severity: Critical
Advisory: GHSA-6v73-fgf6-w5j7
CVE: CVE-2022-22963
CWE: CWE-917, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-04-03
Source: https://github.com/advisories/GHSA-6v73-fgf6-w5j7
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=3.2.0 <3.2.3
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=0 <3.1.7

## Details
In Spring Cloud Function versions 3.1.6, 3.2.2 and older unsupported versions, when using routing functionality it is possible for a user to provide a specially crafted SpEL as a routing-expression that may result in remote code execution and access to local resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22963
- https://github.com/spring-cloud/spring-cloud-function
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0005
- https://tanzu.vmware.com/security/cve-2022-22963
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-java-spring-scf-rce-DQrHhJxH
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-22963
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://packetstormsecurity.com/files/173430/Spring-Cloud-3.2.2-Remote-Command-Execution.html

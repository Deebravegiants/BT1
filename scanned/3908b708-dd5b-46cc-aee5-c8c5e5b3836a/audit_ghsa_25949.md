# [C] Spring Cloud Gateway vulnerable to Code Injection when Gateway Actuator endpoint enabled, exposed, unsecured

## Summary
Severity: Critical
Advisory: GHSA-3gx9-37ww-9qw6
CVE: CVE-2022-22947
CWE: CWE-917, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-3gx9-37ww-9qw6
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-gateway` — affected >=0 <3.0.7
- Maven: `org.springframework.cloud:spring-cloud-gateway` — affected >=3.1.0 <3.1.1

## Details
In Spring Cloud Gateway versions prior to 3.1.1+ and 3.0.7+ , applications are vulnerable to a code injection attack when the Gateway Actuator endpoint is enabled, exposed, and unsecured. A remote attacker could make a maliciously crafted request resulting in arbitrary remote execution on the remote host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22947
- https://tanzu.vmware.com/security/cve-2022-22947
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://packetstormsecurity.com/files/166219/Spring-Cloud-Gateway-3.1.0-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/168742/Spring-Cloud-Gateway-3.1.0-Remote-Code-Execution.html

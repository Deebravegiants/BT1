# [M] SQL Injection in Spring Cloud Task

## Summary
Severity: Medium
Advisory: GHSA-878w-7gxp-mc63
CVE: CVE-2020-5428
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-878w-7gxp-mc63
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-task-dependencies` — affected >=0 <2.2.5

## Details
In applications using Spring Cloud Task 2.2.4.RELEASE and below, may be vulnerable to SQL injection when exercising certain lookup queries in the TaskExplorer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5428
- https://tanzu.vmware.com/security/cve-2020-5428

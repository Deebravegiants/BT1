# [M] Jenkins Datadog Plugin does not perform a permission check in an HTTP endpoint.

## Summary
Severity: Medium
Advisory: GHSA-w3p4-7823-m33q
CVE: CVE-2023-37944
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-w3p4-7823-m33q
Type: github-advisory

## Affected
- Maven: `org.datadog.jenkins.plugins:datadog` — affected >=0 <5.4.2

## Details
Jenkins Datadog Plugin 5.4.1 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Datadog Plugin 5.4.2 requires Overall/Administer permission to access the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37944
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3130
- http://www.openwall.com/lists/oss-security/2023/07/12/2

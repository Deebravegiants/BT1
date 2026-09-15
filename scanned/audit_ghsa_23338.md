# [M] Improper Output Neutralization for Logs in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-rfmp-97jj-h8m6
CVE: CVE-2021-22096
CWE: CWE-117
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rfmp-97jj-h8m6
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.3.0 <5.3.11
- Maven: `org.springframework:spring-core` — affected >=5.2.0 <5.2.18
- Maven: `org.springframework:spring` — affected >=5.2.0 <5.2.18
- Maven: `org.springframework:spring` — affected >=5.3.0 <5.3.11

## Details
In Spring Framework versions 5.3.0 - 5.3.10, 5.2.0 - 5.2.17, and older unsupported versions, it is possible for a user to provide malicious input to cause the insertion of additional log entries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22096
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20211125-0005
- https://tanzu.vmware.com/security/cve-2021-22096
- https://www.oracle.com/security-alerts/cpuapr2022.html

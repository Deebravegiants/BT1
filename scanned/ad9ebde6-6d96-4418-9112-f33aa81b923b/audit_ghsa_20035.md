# [H] Cross-site Scripting in Jenkins Spring Config Plugin

## Summary
Severity: High
Advisory: GHSA-3rrx-364r-6wf6
CVE: CVE-2022-46687
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-3rrx-364r-6wf6
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:spring-config` — affected >=0 <2.0.1

## Details
Jenkins Spring Config Plugin 2.0.0 and earlier does not escape build display names shown on the Spring Config view, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to change build display names. Spring Config Plugin 2.0.1 escapes build display names shown on the Spring Config view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46687
- https://github.com/jenkinsci/spring-config-plugin/commit/89fea88b24f92233ed31050b8e695eb9b502b8c0
- https://github.com/jenkinsci/spring-config-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2814

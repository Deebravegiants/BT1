# [M] Jenkins OpenTelemetry Plugin missing permission check allows capturing credentials

## Summary
Severity: Medium
Advisory: GHSA-f696-867g-2759
CVE: CVE-2025-58460
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-f696-867g-2759
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:opentelemetry` — affected >=0 <3.1543.1545.vf5a

## Details
A missing permission check in Jenkins OpenTelemetry Plugin 3.1543.v8446b_92b_cd64 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58460
- https://github.com/jenkinsci/opentelemetry-plugin/commit/f5a4ec123769096ad9a4930ede56588b0fee40f3
- https://github.com/jenkinsci/opentelemetry-plugin
- https://github.com/jenkinsci/opentelemetry-plugin/releases/tag/3.1543.1545.vf5a_4ec123769
- https://www.jenkins.io/security/advisory/2025-09-03/#SECURITY-3602
- http://www.openwall.com/lists/oss-security/2025/09/03/4

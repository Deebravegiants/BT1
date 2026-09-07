# [M] Incorrect permission checks in Pipeline: Nodes and Processes plugin

## Summary
Severity: Medium
Advisory: GHSA-9r7f-rqhw-j8h8
CVE: CVE-2018-1000015
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9r7f-rqhw-j8h8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-durable-task-step` — affected >=0 <2.18

## Details
On Jenkins instances with Authorize Project plugin, the authentication associated with a build may lack the Computer/Build permission on some agents. This did not prevent the execution of Pipeline `node` blocks on those agents due to incorrect permissions checks in Pipeline: Nodes and Processes plugin 2.17 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000015
- https://jenkins.io/security/advisory/2018-01-22

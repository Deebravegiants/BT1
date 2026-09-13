# [C] Script security sandbox bypass in Matrix Project Plugin

## Summary
Severity: Critical
Advisory: GHSA-qxf8-8837-hq7w
CVE: CVE-2019-1003031
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qxf8-8837-hq7w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-project` — affected >=0 <1.14

## Details
A sandbox bypass vulnerability exists in Jenkins Matrix Project Plugin 1.13 and earlier in pom.xml, src/main/java/hudson/matrix/FilterScript.java that allows attackers with Job/Configure permission to execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003031
- https://github.com/jenkinsci/matrix-project-plugin/commit/765fc39694b31f8dd6e3d27cf51d1708b5df2be7
- https://access.redhat.com/errata/RHSA-2019:0739
- https://github.com/jenkinsci/matrix-project-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1339
- http://www.securityfocus.com/bid/107476

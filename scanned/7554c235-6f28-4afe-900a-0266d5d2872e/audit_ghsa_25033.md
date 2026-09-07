# [M] XSS vulnerability in Jenkins Warnings Next Generation Plugin

## Summary
Severity: Medium
Advisory: GHSA-cqp7-hwm3-cfg7
CVE: CVE-2019-1003023
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cqp7-hwm3-cfg7
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=0 <2.0.0

## Details
A cross-site scripting vulnerability exists in Jenkins Warnings Next Generation Plugin 1.0.1 and earlier in src/main/java/io/jenkins/plugins/analysis/core/model/DetailsTableModel.java, src/main/java/io/jenkins/plugins/analysis/core/model/SourceDetail.java, src/main/java/io/jenkins/plugins/analysis/core/model/SourcePrinter.java, src/main/java/io/jenkins/plugins/analysis/core/util/Sanitizer.java, src/main/java/io/jenkins/plugins/analysis/warnings/DuplicateCodeScanner.java that allows attackers with the ability to control warnings parser input to have Jenkins render arbitrary HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003023
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1271

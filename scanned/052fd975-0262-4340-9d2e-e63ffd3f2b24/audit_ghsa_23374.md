# [C] Sandbox bypass in ontrack Jenkins Plugin

## Summary
Severity: Critical
Advisory: GHSA-qw28-g63m-jxqv
CVE: CVE-2019-10306
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qw28-g63m-jxqv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ontrack` — affected >=0 <3.4.1

## Details
A sandbox bypass vulnerability in Jenkins ontrack Plugin 3.4 and earlier allowed attackers with control over ontrack DSL definitions to execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10306
- https://github.com/jenkinsci/ontrack-plugin/commit/7f0f806c18fdd6043103d848ba4c813cb805dd85
- https://github.com/jenkinsci/ontrack-plugin
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-1341
- http://www.securityfocus.com/bid/108045

# [M] Cross-site Scripting in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-hv45-5j9h-7fhg
CVE: CVE-2018-1000407
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hv45-5j9h-7fhg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.138.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.140 <2.146

## Details
A cross-site scripting vulnerability exists in Jenkins 2.145 and earlier, LTS 2.138.1 and earlier in core/src/main/java/hudson/model/Api.java that allows attackers to specify URLs to Jenkins that result in rendering arbitrary attacker-controlled HTML by Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000407
- https://github.com/jenkinsci/jenkins/commit/df87e12ddcfeafdba6e0de0e07b3e21f8473ece6
- https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1129
- http://www.securityfocus.com/bid/106532

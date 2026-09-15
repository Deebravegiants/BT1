# [H] XML External Entity processing vulnerability in Pipeline Maven Integration Jenkins Plugin

## Summary
Severity: High
Advisory: GHSA-6755-jgp4-8q7h
CVE: CVE-2019-10327
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6755-jgp4-8q7h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-maven` — affected >=0 <3.7.1

## Details
An XML external entities (XXE) vulnerability in Jenkins Pipeline Maven Integration Plugin 1.7.0 and earlier allowed attackers able to control a temporary directory's content on the agent running the Maven build to have Jenkins parse a maliciously crafted XML file that uses external entities for extraction of secrets from the Jenkins master, server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10327
- https://github.com/jenkinsci/pipeline-maven-plugin/commit/e7cb858852c05d2423e3fd9922a090982dcd6392
- https://github.com/jenkinsci/pipeline-maven-plugin/tree/master/pipeline-maven
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1409
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540

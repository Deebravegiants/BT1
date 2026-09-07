# [M] Agent-to-controller security bypass vulnerability in Jenkins Compuware Xpediter Code Coverage Plugin

## Summary
Severity: Medium
Advisory: GHSA-mfcw-83qg-4vw3
CVE: CVE-2022-43424
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-mfcw-83qg-4vw3
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-xpediter-code-coverage` — affected >=0 <1.0.8

## Details
Compuware Xpediter Code Coverage Plugin 1.0.7 and earlier implements an agent/controller message that does not limit where it can be executed.

It allows attackers able to control agent processes to obtain the values of Java system properties from the Jenkins controller process.

This vulnerability is only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3).

Compuware Xpediter Code Coverage Plugin 1.0.8 restricts execution of the agent/controller message to agents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43424
- https://github.com/jenkinsci/compuware-xpediter-code-coverage-plugin/commit/e506fc9e77a2609f6a5aa331e052d35be652071c
- https://github.com/jenkinsci/compuware-xpediter-code-coverage-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2627
- http://www.openwall.com/lists/oss-security/2022/10/19/3

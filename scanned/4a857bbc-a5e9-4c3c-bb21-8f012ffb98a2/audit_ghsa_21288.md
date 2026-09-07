# [H] Agent-to-controller security bypass vulnerabilities in Jenkins Compuware Topaz for Total Test Plugin

## Summary
Severity: High
Advisory: GHSA-xp3r-9wx8-q2mm
CVE: CVE-2022-43428
CWE: CWE-610, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-xp3r-9wx8-q2mm
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-for-total-test` — affected >=0 <2.4.9

## Details
Jenkins Compuware Topaz for Total Test Plugin 2.4.8 and earlier implements an agent/controller message that does not limit where it can be executed, allowing attackers able to control agent processes to obtain the values of Java system properties from the Jenkins controller process.

These vulnerabilities are only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43428
- https://github.com/jenkinsci/compuware-topaz-for-total-test-plugin/commit/5fca6eb21599f8f27323dfa17a6e44f8176ca551
- https://github.com/jenkinsci/compuware-topaz-for-total-test-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2624
- http://www.openwall.com/lists/oss-security/2022/10/19/3

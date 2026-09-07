# [M] Arbitrary file read vulnerability in Jenkins Continuous Integration with Toad Edge Plugin

## Summary
Severity: Medium
Advisory: GHSA-8p4x-fq8v-xhv4
CVE: CVE-2022-28146
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-8p4x-fq8v-xhv4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ci-with-toad-edge` — affected >=0 <2.4

## Details
Jenkins Continuous Integration with Toad Edge Plugin 2.3 and earlier allows attackers with Item/Configure permission to read arbitrary files on the Jenkins controller by specifying an input folder on the Jenkins controller as a parameter to its build steps.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28146
- https://github.com/jenkinsci/ci-with-toad-edge-plugin/commit/49d4b855773ed4bbc58fc510149ec24d504f80d4
- https://github.com/jenkinsci/ci-with-toad-edge-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2633
- http://www.openwall.com/lists/oss-security/2022/03/29/1

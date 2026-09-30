# [M] Arbitrary file write vulnerability in Jenkins Cobertura Plugin

## Summary
Severity: Medium
Advisory: GHSA-m935-chfp-9f63
CVE: CVE-2020-2139
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m935-chfp-9f63
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cobertura` — affected >=0 <1.16

## Details
An arbitrary file write vulnerability in Jenkins Cobertura Plugin 1.15 and earlier allows attackers able to control the coverage report file contents to overwrite any file on the Jenkins master file system. Cobertura Plugin 1.16 sanitizes the file paths to prevent escape from the base directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2139
- https://github.com/jenkinsci/cobertura-plugin/commit/ea41b3f86a24ab398a588bde6a4eada869bed391
- https://github.com/jenkinsci/cobertura-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1668
- http://www.openwall.com/lists/oss-security/2020/03/09/1

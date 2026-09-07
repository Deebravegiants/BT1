# [M] Jenkins Gem Publisher Plugin stores credentials as plaintext

## Summary
Severity: Medium
Advisory: GHSA-6pqm-pp65-mc26
CVE: CVE-2019-10426
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6pqm-pp65-mc26
Type: github-advisory

## Affected
- Maven: `net.arangamani.jenkins:gem-publisher` — affected >=0

## Details
Jenkins Gem Publisher Plugin stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10426
- https://github.com/jenkinsci/gem-publisher-plugin
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1573
- http://www.openwall.com/lists/oss-security/2019/09/25/3

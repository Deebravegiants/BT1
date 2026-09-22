# [H] OS command execution vulnerability in Jenkins Docker Commons Plugin

## Summary
Severity: High
Advisory: GHSA-jpxj-vgq5-prjc
CVE: CVE-2022-20617
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-jpxj-vgq5-prjc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:docker-commons` — affected >=0 <1.18

## Details
Jenkins Docker Commons Plugin 1.17 and earlier does not sanitize the name of an image or a tag, resulting in an OS command execution vulnerability exploitable by attackers with Item/Configure permission or able to control the contents of a previously configured job's SCM repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20617
- https://github.com/jenkinsci/docker-commons-plugin/commit/c069b79c31c5aa80a01b0c462f0dc6b41751f059
- https://github.com/jenkinsci/docker-commons-plugin
- https://plugins.jenkins.io/docker-commons
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-1878
- http://www.openwall.com/lists/oss-security/2022/01/12/6

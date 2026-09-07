# [M] Missing permission check in Jenkins requests-plugin Plugin allows viewing pending requests

## Summary
Severity: Medium
Advisory: GHSA-c4c3-3cgh-vvrh
CVE: CVE-2021-21674
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c4c3-3cgh-vvrh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:requests` — affected >=0 <2.2.7

## Details
Jenkins requests-plugin Plugin 2.2.6 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to view the list of pending requests.

Jenkins requests-plugin Plugin 2.2.7 requires Overall/Administer permission to view the list of pending requests.

The previous sentence originally stated that Overall/Read permission was newly required. This statement was incorrect and has been fixed on 2021-07-05.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21674
- https://github.com/jenkinsci/requests-plugin/commit/eb8ae816bbe734203debe323c578adc41baac5f4
- https://github.com/jenkinsci/requests-plugin
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-1995
- http://www.openwall.com/lists/oss-security/2021/06/30/1

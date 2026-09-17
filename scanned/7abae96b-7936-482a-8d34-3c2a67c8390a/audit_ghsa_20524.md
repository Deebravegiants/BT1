# [H] Path Traversal in Jenkins Warnings Next Generation Plugin

## Summary
Severity: High
Advisory: GHSA-rvh4-g2rj-hr9c
CVE: CVE-2022-23107
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-rvh4-g2rj-hr9c
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=9.8.0 <9.10.3
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=9.6.0 <9.7.1
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=9.1.0 <9.5.2
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=0 <9.0.2

## Details
Jenkins Warnings Next Generation Plugin prior to 9.10.3, 9.7.1, 9.5.2, and 9.0.2 does not restrict the name of a file when configuring a custom ID.

This allows attackers with Item/Configure permission to write and read specific files with a hard-coded suffix on the Jenkins controller file system.

Jenkins Warnings Next Generation Plugin 9.10.3, 9.7.1, 9.5.2, and 9.0.2 checks for the presence of prohibited directory separator characters in the custom ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23107
- https://github.com/CVEProject/cvelist/blob/36f932156733baab1b13868be4338de406a1dec7/2022/23xxx/CVE-2022-23107.json
- https://github.com/jenkinsci/warnings-ng-plugin
- https://github.com/jenkinsci/warnings-ng-plugin/releases/tag/v9.10.3
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2090
- http://www.openwall.com/lists/oss-security/2022/01/12/6

# [H] Denial of service in Jenkins Core

## Summary
Severity: High
Advisory: GHSA-h76p-mc68-jv3p
CVE: CVE-2023-27901
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-h76p-mc68-jv3p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.388 <2.394
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.375.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.376 <2.387.1

## Details
Jenkins 2.393 and earlier, LTS 2.375.3 and earlier uses the Apache Commons FileUpload library without specifying limits for the number of request parts introduced in version 1.5 for CVE-2023-24998 in org.kohsuke.stapler.RequestImpl, allowing attackers to trigger a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27901
- https://github.com/jenkinsci/jenkins/commit/b70f4cb5892bd6059a45b5f156f019ce572adb08
- https://github.com/CVEProject/cvelist/blob/master/2023/27xxx/CVE-2023-27901.json
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-3030

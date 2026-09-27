# [M] Jenkins is missing a permission check in the authenticated users' profile menu 

## Summary
Severity: Medium
Advisory: GHSA-223m-4rfp-646h
CVE: CVE-2025-59475
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-223m-4rfp-646h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.516.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.517 <2.528

## Details
Jenkins 2.527 and earlier, LTS 2.516.2 and earlier does not perform a permission check for the authenticated user profile dropdown menu. This allows attackers without Overall/Read permission to obtain limited information about the Jenkins configuration by listing available options in this menu (e.g., whether Credentials Plugin is installed).

Jenkins 2.528, LTS 2.516.3 requires Overall/Read permission to list various items in authenticated user profile dropdown menus.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59475
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-09-17/#SECURITY-3625
- http://www.openwall.com/lists/oss-security/2025/09/17/1

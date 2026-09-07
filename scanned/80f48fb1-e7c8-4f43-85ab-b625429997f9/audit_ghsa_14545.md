# [M] Incorrect Permission Preservation in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-cj6r-8pxj-5jv6
CVE: CVE-2023-27902
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-cj6r-8pxj-5jv6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.376 <2.387.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.375.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.388 <2.394

## Details
Jenkins uses temporary directories adjacent to workspace directories, usually with the @tmp name suffix, to store temporary files related to the build. In pipelines, these temporary directories are adjacent to the current working directory when operating in a subdirectory of the automatically allocated workspace. Jenkins-controlled processes, like SCMs, may store credentials in these directories.

Jenkins 2.393 and earlier, LTS 2.375.3 and earlier, and prior to LTS 2.387.1 shows these temporary directories when viewing job workspaces, which allows attackers with Item/Workspace permission to access their contents.

Jenkins 2.394, LTS 2.375.4, and LTS 2.387.1 does not list these temporary directories in job workspaces.

As a workaround, do not grant Item/Workspace permission to users who lack Item/Configure permission, if you’re concerned about this issue but unable to immediately update Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27902
- https://github.com/jenkinsci/jenkins/commit/80452662b31ac6c9f4418cffae1af6af4daf479a
- https://github.com/CVEProject/cvelist/blob/master/2023/27xxx/CVE-2023-27902.json
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-1807

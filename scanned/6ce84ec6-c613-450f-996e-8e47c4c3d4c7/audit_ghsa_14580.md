# [H] Incorrect Authorization in Jenkins Core

## Summary
Severity: High
Advisory: GHSA-hf9h-vv4m-2f33
CVE: CVE-2023-27899
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-hf9h-vv4m-2f33
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.376 <2.387.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.375.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.388 <2.394

## Details
Jenkins creates a temporary file when a plugin is uploaded from an administrator’s computer.

Jenkins 2.393 and earlier, LTS 2.375.3 and earlier, and prior to LTS 2.387.1 creates this temporary file in the system temporary directory with the default permissions for newly created files.

If these permissions are overly permissive, they may allow attackers with access to the Jenkins controller file system to read and write the file before it is installed in Jenkins, potentially resulting in arbitrary code execution.

This vulnerability only affects operating systems using a shared temporary directory for all users (typically Linux). Additionally, the default permissions for newly created files generally only allows attackers to read the temporary file.
Jenkins 2.394, LTS 2.375.4, and LTS 2.387.1 creates the temporary file with more restrictive permissions.

As a workaround, you can set a different path as your default temporary directory using the Java system property java.io.tmpdir, if you’re concerned about this issue but unable to immediately update Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27899
- https://github.com/jenkinsci/jenkins/commit/f39c11fa27b14923260c4c9b896f0f373e2a0a17
- https://github.com/CVEProject/cvelist/blob/master/2023/27xxx/CVE-2023-27899.json
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-2823

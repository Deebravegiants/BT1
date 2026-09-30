# [H] Jenkins temporary plugin file created with insecure permissions 

## Summary
Severity: High
Advisory: GHSA-55wp-3pq4-w8p9
CVE: CVE-2023-43496
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-55wp-3pq4-w8p9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.50 <2.414.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.415 <2.424

## Details
Jenkins creates a temporary file when a plugin is deployed directly from a URL.

Jenkins 2.423 and earlier, LTS 2.414.1 and earlier creates this temporary file in the system temporary directory with the default permissions for newly created files.

If these permissions are overly permissive, they may allow attackers with access to the Jenkins controller file system to read and write the file before it is installed in Jenkins, potentially resulting in arbitrary code execution.

This vulnerability only affects operating systems using a shared temporary directory for all users (typically Linux). Additionally, the default permissions for newly created files generally only allow attackers to read the temporary file, but not write to it.

This issue complements SECURITY-2823, which affected plugins uploaded from an administrator’s computer.
Jenkins 2.424, LTS 2.414.2 creates the temporary file in a subdirectory with more restrictive permissions.

As a workaround, you can change your default temporary-file directory using the Java system property java.io.tmpdir, if you’re concerned about this issue but unable to immediately update Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43496
- https://github.com/jenkinsci/jenkins/commit/df7c4ccda8976c06bf31b8fb9938f26fc38501ca
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3072
- http://www.openwall.com/lists/oss-security/2023/09/20/5

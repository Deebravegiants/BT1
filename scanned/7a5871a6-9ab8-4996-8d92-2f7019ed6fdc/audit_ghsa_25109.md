# [H] Agent-to-controller access control allowed writing to sensitive directory used by Jenkins Pipeline: Shared Groovy Libraries Plugin

## Summary
Severity: High
Advisory: GHSA-c5r9-rx53-q3gf
CVE: CVE-2021-21696
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c5r9-rx53-q3gf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.303.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.304 <2.319

## Details
Jenkins 2.318 and earlier, LTS 2.303.2 and earlier does not limit agent read/write access to the `libs/` directory inside build directories when using the `FilePath` APIs. This directory is used by the Pipeline: Shared Groovy Libraries Plugin to store copies of shared libraries.

This allows attackers in control of agent processes to replace the code of a trusted library with a modified variant, resulting in unsandboxed code execution in the Jenkins controller process.

Jenkins 2.319, LTS 2.303.3 prohibits agent read/write access to the `libs/` directory inside build directories.

If you are unable to immediately upgrade to Jenkins 2.319, LTS 2.303.3, you can install the [Remoting Security Workaround Plugin](https://www.jenkins.io/redirect/remoting-security-workaround/). It will prevent all agent-to-controller file access using FilePath APIs. Because it is more restrictive than Jenkins 2.319, LTS 2.303.3, more plugins are incompatible with it. Make sure to read the plugin documentation before installing it.

It is not easily possible to [customize the file access rules](https://www.jenkins.io/doc/book/security/controller-isolation/agent-to-controller/#file-access-rules) to prohibit access to the `libs/` directory specifically, as built-in rules (granting access to `<BUILDDIR>` contents) would take precedence over a custom rule prohibiting access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21696
- https://github.com/jenkinsci/jenkins/commit/93451e20c20cfd84badeb0f37c38d4c0c7a5dad3
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2423
- http://www.openwall.com/lists/oss-security/2021/11/04/3

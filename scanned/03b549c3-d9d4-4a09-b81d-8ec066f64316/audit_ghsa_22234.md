# [C] Multiple vulnerabilities allow bypassing path filtering of agent-to-controller access control in Jenkins

## Summary
Severity: Critical
Advisory: GHSA-929w-q433-4h9x
CVE: CVE-2021-21693
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-929w-q433-4h9x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.303.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.304 <2.319

## Details
The agent-to-controller security subsystem limits which files on the Jenkins controller can be accessed by agent processes.

Multiple vulnerabilities in the file path filtering implementation of Jenkins 2.318 and earlier, LTS 2.303.2 and earlier allow agent processes to read and write arbitrary files on the Jenkins controller file system, and obtain some information about Jenkins controller file systems.

SECURITY-2539 / CVE-2021-21693: When creating temporary files, permission to create files is only checked after they’ve been created.

We expect that most of these vulnerabilities have been present since [SECURITY-144 was addressed in the 2014-10-30 security advisory](https://www.jenkins.io/security/advisory/2014-10-30/).

Jenkins 2.319, LTS 2.303.3 addresses these security vulnerabilities.

SECURITY-2539 / CVE-2021-21693: When creating temporary files, permission to create files is checked before they are created based on an artificial path.

As some common operations are now newly subject to access control, it is expected that plugins sending commands from agents to the controller may start failing. Additionally, the newly introduced path canonicalization means that instances using a custom builds directory ([Java system property jenkins.model.Jenkins.buildsDir](https://www.jenkins.io/doc/book/managing/system-properties/#jenkins-model-jenkins-buildsdir)) or partitioning `JENKINS_HOME` using symbolic links may fail access control checks. See [the documentation](https://www.jenkins.io/doc/book/security/controller-isolation/agent-to-controller/#file-access-rules) for how to customize the configuration in case of problems.

If you are unable to immediately upgrade to Jenkins 2.319, LTS 2.303.3, you can install the [Remoting Security Workaround Plugin](https://www.jenkins.io/redirect/remoting-security-workaround/). It will prevent all agent-to-controller file access using `FilePath` APIs. Because it is more restrictive than Jenkins 2.319, LTS 2.303.3, more plugins are incompatible with it. Make sure to read the plugin documentation before installing it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21693
- https://github.com/jenkinsci/jenkins/commit/104c751d907919dd53f5090f84d53c671a66457b
- https://github.com/jenkinsci/jenkins/commit/5a245e42979abe4a26d41727c839521e36cedd74
- https://github.com/jenkinsci/jenkins/commit/63cde2daadc705edf086f2213b48c8c547f98358
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455

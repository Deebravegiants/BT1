# [C] Agent-to-controller access control allows reading/writing most content of build directories in Jenkins

## Summary
Severity: Critical
Advisory: GHSA-cv2w-q8c3-xjv7
CVE: CVE-2021-21697
CWE: CWE-184
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cv2w-q8c3-xjv7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.303.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.304 <2.319

## Details
Agents are allowed some limited access to files on the Jenkins controller file system. The directories agents are allowed to access in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier include the directories storing build-related information, intended to allow agents to store build-related metadata during build execution. As a consequence, this allows any agent to read and write the contents of any build directory stored in Jenkins with very few restrictions (`build.xml` and some Pipeline-related metadata).

Jenkins 2.319, LTS 2.303.3 prevents agents from accessing contents of build directories unless it’s for builds currently running on the agent attempting to access the directory.

Update [Pipeline: Nodes and Processes](https://plugins.jenkins.io/workflow-durable-task-step/) to version 2.40 or newer for Jenkins to associate Pipeline `node` blocks with the agent they’re running on for this fix.

If you are unable to immediately upgrade to Jenkins 2.319, LTS 2.303.3, you can install the [Remoting Security Workaround Plugin](https://www.jenkins.io/redirect/remoting-security-workaround/). It will prevent all agent-to-controller file access using `FilePath` APIs. Because it is more restrictive than Jenkins 2.319, LTS 2.303.3, more plugins are incompatible with it. Make sure to read the plugin documentation before installing it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21697
- https://github.com/jenkinsci/jenkins/commit/cf388d2a04e6016d23eb93fa3cc804f2554b98f0
- https://github.com/jenkinsci/jenkins/commit/eae33841b587da787f37d5b6c8451d483edc04d9
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2428
- http://www.openwall.com/lists/oss-security/2021/11/04/3

# [H] Jenkins Remoting library arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-h856-ffvv-xvr4
CVE: CVE-2024-43044
CWE: CWE-22, CWE-754
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-h856-ffvv-xvr4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:remoting` — affected >=0 <3206.3208
- Maven: `org.jenkins-ci.main:remoting` — affected >=3248 <3248.3250
- Maven: `org.jenkins-ci.main:remoting` — affected >=3256 <3256.3258
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.452.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.460 <2.462.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.470 <2.471

## Details
Jenkins uses the Remoting library (typically `agent.jar` or `remoting.jar`) for the communication between controller and agents. This library allows agents to load classes and classloader resources from the controller, so that Java objects sent from the controller (build steps, etc.) can be executed on agents.

In addition to individual class and resource files, Remoting also allows Jenkins plugins to transmit entire jar files to agents using the `Channel#preloadJar` API. As of publication of this advisory, this feature is used by the following plugins distributed by the Jenkins project: bouncycastle API, Groovy, Ivy, TeamConcert

In Remoting 3256.v88a_f6e922152 and earlier, except 3206.3208.v409508a_675ff and 3248.3250.v3277a_8e88c9b_, included in Jenkins 2.470 and earlier, LTS 2.452.3 and earlier, calls to `Channel#preloadJar` result in the retrieval of files from the controller by the agent using `ClassLoaderProxy#fetchJar`. Additionally, the implementation of `ClassLoaderProxy#fetchJar` invoked on the controller does not restrict paths that agents could request to read from the controller file system.

This allows agent processes, code running on agents, and attackers with Agent/Connect permission to read arbitrary files from the Jenkins controller file system.

The Remoting library in Jenkins 2.471, LTS 2.452.4, LTS 2.462.1 now sends jar file contents with `Channel#preloadJar` requests, the only use case of `ClassLoaderProxy#fetchJar` in agents, so that agents do not need to request jar file contents from controllers anymore.

To retain compatibility with older versions of Remoting in combination with the plugins listed above, `ClassLoaderProxy#fetchJar` is retained and otherwise unused, just deprecated. Its implementation in Jenkins 2.471, LTS 2.452.4, LTS 2.462.1 was changed so that it is now limited to retrieving jar files referenced in the core classloader or any plugin classloader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43044
- https://github.com/jenkinsci/jenkins/commit/3f54c41b40db9e4ae7afa4209bc1ea91bb9175c0
- https://github.com/jenkinsci/jenkins/commit/5d26b53ad3a5cd8c4a060eef4f56d75e65ca17a5
- https://github.com/jenkinsci/jenkins/commit/cec49ce5d58048f66ac3fa88409a0d38dec09bf0
- https://github.com/jenkinsci/remoting/commit/3277a8e88c9b807b9a989bd7e9176d2ec9834e47
- https://github.com/jenkinsci/remoting/commit/409508a675ffc4ed9681e30bb46c8d9cb375b78c
- https://github.com/jenkinsci/remoting/commit/858f3c9af69d4d216b26551ea51dde6e67479bb3
- https://github.com/jenkinsci/remoting
- https://www.jenkins.io/security/advisory/2024-08-07/#SECURITY-3430

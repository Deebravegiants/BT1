# [H] Path traversal in Jenkins Git Mercurial and Repo Plugins

## Summary
Severity: High
Advisory: GHSA-84cm-vjwm-m979
CVE: CVE-2022-30947
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-84cm-vjwm-m979
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <4.11.2
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=0 <2.16.1
- Maven: `org.jenkins-ci.plugins:repo` — affected >=0 <1.15.0

## Details
Jenkins SCMs support a number of different URL schemes, including local file system paths (e.g. using `file:` URLs).

Historically in Jenkins, only agents checked out from SCM, and if multiple projects share the same agent, there is no expected isolation between builds besides using different workspaces unless overridden. Some Pipeline-related features check out SCMs from the Jenkins controller as well.

This allows attackers able to configure pipelines to check out some SCM repositories stored on the Jenkins controller’s file system using local paths as SCM URLs, obtaining limited information about other projects' SCM contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30947
- https://github.com/jenkinsci/git-plugin/commit/b295606e0b865c298fde27bea14f9b7535a976e6
- https://github.com/jenkinsci/mercurial-plugin/commit/55904fbb8c9d3e0b36fc26330374904cb68e8758
- https://github.com/jenkinsci/repo-plugin/commit/3c8e6236b1088fc138a1a3e6af5ebbcb8b616f2f
- https://github.com/jenkinsci/git-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2478
- http://www.openwall.com/lists/oss-security/2022/05/17/8

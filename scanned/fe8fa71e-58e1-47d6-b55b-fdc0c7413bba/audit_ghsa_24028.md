# [M] Server-Side Request Forgery in Jenkins Git Plugin

## Summary
Severity: Medium
Advisory: GHSA-53wf-vqf9-cgf2
CVE: CVE-2018-1000182
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-53wf-vqf9-cgf2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <3.9.1

## Details
A server-side request forgery vulnerability exists in Jenkins Git Plugin 3.9.0 and older in AssemblaWeb.java, GitBlitRepositoryBrowser.java, Gitiles.java, TFS2013GitRepositoryBrowser.java, ViewGitWeb.java that allows attackers with Overall/Read access to cause Jenkins to send a GET request to a specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000182
- https://github.com/jenkinsci/git-plugin/commit/87a03f3d9c4a0c0a918d91e173b200a6a3b237a7
- https://github.com/jenkinsci/git-plugin
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-810

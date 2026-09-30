# [M] Webhook endpoint discloses job names to unauthorized users in Jenkins Mercurial Plugin

## Summary
Severity: Medium
Advisory: GHSA-j7pg-863g-22p6
CVE: CVE-2022-43410
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-j7pg-863g-22p6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=0 <1260.vdfb_723cdcc81

## Details
Mercurial Plugin provides a webhook endpoint at `/mercurial/notifyCommit` that can be used to notify Jenkins of changes to an SCM repository. This endpoint receives a repository URL, and Jenkins will schedule polling for all jobs configured with the specified repository. It can be accessed with GET requests and without authentication.

In Mercurial Plugin 1251.va_b_121f184902 and earlier, the output of the webhook endpoint will provide information about which jobs were triggered or scheduled for polling, including jobs the user has no permission to access. This allows attackers with knowledge of Mercurial repository URLs to obtain information about the existence of jobs configured with this Mercurial repository.

Mercurial Plugin 1260.vdfb_723cdcc81 does not provide the names of jobs for which polling is triggered unless the user has the appropriate Item/Read permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43410
- https://github.com/jenkinsci/mercurial-plugin/commit/dfb723cdcc815875cdf63abd32e314ced5e95ac9
- https://github.com/jenkinsci/mercurial-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2831
- http://www.openwall.com/lists/oss-security/2022/10/19/3

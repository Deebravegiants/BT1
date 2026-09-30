# [M] Lack of authentication mechanism in Jenkins Git Plugin webhook

## Summary
Severity: Medium
Advisory: GHSA-8xwj-2wgh-gprh
CVE: CVE-2022-36882
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-8xwj-2wgh-gprh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <4.11.4

## Details
Git Plugin provides a webhook endpoint at `/git/notifyCommit` that can be used to notify Jenkins of changes to an SCM repository. For its most basic functionality, this endpoint receives a repository URL, and Jenkins will schedule polling for all jobs configured with the specified repository. In Git Plugin 4.11.3 and earlier, this endpoint can be accessed with GET requests and without authentication.

This webhook endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Git Plugin 4.11.4 requires a `token` parameter which will act as an authentication for the webhook endpoint. While GET requests remain allowed, attackers would need to be able to provide a webhook token. For more information see [the plugin documentation](https://github.com/jenkinsci/git-plugin/#push-notification-from-repository).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36882
- https://github.com/jenkinsci/git-plugin/commit/b46165c74a0bf15e08763de2e506005624d5d238
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-284
- http://www.openwall.com/lists/oss-security/2022/07/27/1

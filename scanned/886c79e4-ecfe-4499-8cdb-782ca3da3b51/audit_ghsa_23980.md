# [H] Improper authorization of users and groups with the same base name in Jenkins GitLab Authentication Plugin

## Summary
Severity: High
Advisory: GHSA-qq38-mxpq-rrpj
CVE: CVE-2020-2228
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qq38-mxpq-rrpj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-oauth` — affected >=0 <1.6

## Details
GitLab Authentication Plugin 1.5 and earlier does not differentiate between user names and hierarchical group names when performing authorization. This allows an attacker with permissions to create groups in GitLab to gain the privileges granted to another user or group.

GitLab Authentication Plugin 1.6 performs user name and group name authorization checks using the appropriate GitLab APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2228
- https://github.com/jenkinsci/gitlab-oauth-plugin
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1792
- http://www.openwall.com/lists/oss-security/2020/07/15/5

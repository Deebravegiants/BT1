# [H] Jenkins Gitlab Authentication Plugin vulnerable to Session Fixation

## Summary
Severity: High
Advisory: GHSA-682g-c99v-9r2g
CVE: CVE-2019-10371
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-682g-c99v-9r2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-oauth` — affected >=0 <1.5

## Details
A session fixation vulnerability in Jenkins Gitlab Authentication Plugin 1.4 and earlier in GitLabSecurityRealm.java allows unauthorized attackers to impersonate another user if they can control the pre-authentication session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10371
- https://github.com/jenkinsci/gitlab-oauth-plugin/commit/695ce63fddb3567cf8d87339ddc1fa3b67ae2db8
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-795
- http://www.openwall.com/lists/oss-security/2019/08/07/1

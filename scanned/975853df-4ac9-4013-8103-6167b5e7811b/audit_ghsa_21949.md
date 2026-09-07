# [M] Open redirect vulnerability in Jenkins GitLab Authentication Plugin

## Summary
Severity: Medium
Advisory: GHSA-mvq8-hgxh-4v2g
CVE: CVE-2022-25196
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-mvq8-hgxh-4v2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-oauth` — affected >=0

## Details
Jenkins GitLab Authentication Plugin 1.13 and earlier records the HTTP `Referer` header as part of the URL query parameters when the authentication process starts, allowing attackers with access to Jenkins to craft a URL that will redirect users to an attacker-specified URL after logging in.

This issue is caused by an incomplete fix of [SECURITY-796](https://www.jenkins.io/security/advisory/2019-08-07/#SECURITY-796).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25196
- https://github.com/jenkinsci/gitlab-oauth-plugin
- https://www.jenkins.io/security/advisory/2019-08-07/#SECURITY-796
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-1833
- http://www.openwall.com/lists/oss-security/2022/02/15/2

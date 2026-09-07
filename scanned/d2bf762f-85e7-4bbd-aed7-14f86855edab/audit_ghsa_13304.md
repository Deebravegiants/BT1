# [M] CSRF vulnerability in GitLab Authentication Plugin

## Summary
Severity: Medium
Advisory: GHSA-cg6r-gqvc-r396
CVE: CVE-2023-39153
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-cg6r-gqvc-r396
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-oauth` — affected >=0 <1.18

## Details
GitLab Authentication Plugin 1.17.1 and earlier does not implement a state parameter in its OAuth flow, a unique and non-guessable value associated with each authentication request.

This vulnerability allows attackers to trick users into logging in to the attacker’s account.

GitLab Authentication Plugin 1.18 implements a state parameter in its OAuth flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39153
- https://github.com/jenkinsci/gitlab-oauth-plugin/commit/d5bdf767e6be2efa2e9d8f8cf99b98726bb5f29d
- https://github.com/jenkinsci/gitlab-oauth-plugin
- https://www.jenkins.io/security/advisory/2023-07-26/#SECURITY-2696
- http://www.openwall.com/lists/oss-security/2023/07/26/2

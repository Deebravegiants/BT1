# [M] Jenkins Gitea Plugin vulnerable to Cleartext Transmission of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-x3qh-53qf-jxq9
CVE: CVE-2022-46685
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-x3qh-53qf-jxq9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitea` — affected >=0 <1.4.5

## Details
In Jenkins Gitea Plugin 1.4.4 and earlier, the implementation of Gitea personal access tokens did not support credentials masking, potentially exposing them through the build log.

Gitea Plugin 1.4.5 adds support for masking of Gitea personal access tokens.

Administrators unable to update are advised to use SSH checkout instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46685
- https://github.com/jenkinsci/gitea-plugin/commit/b3b2bd869b91f9f1312bbbbf6128cad2cd86bd8c
- https://github.com/jenkinsci/gitea-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2661

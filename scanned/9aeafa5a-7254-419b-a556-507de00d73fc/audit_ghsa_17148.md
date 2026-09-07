# [H] Jenkins GitBucket Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-5j74-g3c5-wqww
CVE: CVE-2024-28157
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-5j74-g3c5-wqww
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitbucket` — affected >=0

## Details
Jenkins GitBucket Plugin 0.8 and earlier does not sanitize Gitbucket URLs on build views, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28157
- https://github.com/jenkinsci/gitbucket-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3249
- http://www.openwall.com/lists/oss-security/2024/03/06/3

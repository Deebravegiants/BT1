# [M] Jenkins Tuleap Git Branch Source Plugin allows unauthenticated attackers to trigger Tuleap projects whose configured repo matches attacker-specified value

## Summary
Severity: Medium
Advisory: GHSA-73v5-w6fg-2m44
CVE: CVE-2022-43421
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-73v5-w6fg-2m44
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:tuleap-git-branch-source` — affected >=0 <3.2.5

## Details
A missing permission check in Jenkins Tuleap Git Branch Source Plugin 3.2.4 and earlier allows unauthenticated attackers to trigger Tuleap projects whose configured repository matches the attacker-specified value. Tuleap Git Branch Source Plugin 3.2.5 requires a token to access the webhook endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43421
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2852
- http://www.openwall.com/lists/oss-security/2022/10/19/3

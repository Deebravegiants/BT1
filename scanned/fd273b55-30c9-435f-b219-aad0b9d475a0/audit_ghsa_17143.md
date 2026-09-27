# [M] Jenkins Bitbucket Branch Source Plugin has incorrect trust policy behavior for pull requests

## Summary
Severity: Medium
Advisory: GHSA-m4rm-x2rr-357w
CVE: CVE-2024-28152
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-m4rm-x2rr-357w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=0 <871.v28d74e8b_4226

## Details
In Jenkins Bitbucket Branch Source Plugin 866.vdea_7dcd3008e and earlier, except 848.850.v6a_a_2a_234a_c81, when discovering pull requests from forks, the trust policy "Forks in the same account" allows changes to Jenkinsfiles from users without write access to the project when using Bitbucket Server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28152
- https://github.com/jenkinsci/bitbucket-branch-source-plugin/commit/28d74e8b4226bfc7524b412e34f7090784cc1a08
- https://github.com/jenkinsci/bitbucket-branch-source-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3300
- http://www.openwall.com/lists/oss-security/2024/03/06/3

# [H] SSRF vulnerability in Jenkins Bitbucket Push and Pull Request Plugin allows capturing credentials

## Summary
Severity: High
Advisory: GHSA-vrpg-c7c4-8mpx
CVE: CVE-2023-41937
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-vrpg-c7c4-8mpx
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:bitbucket-push-and-pull-request` — affected >=2.4.0 <2.8.4

## Details
Jenkins Bitbucket Push and Pull Request Plugin 2.4.0 through 2.8.3 (both inclusive) trusts values provided in the webhook payload, including certain URLs, and uses configured Bitbucket credentials to connect to those URLs, allowing attackers to capture Bitbucket credentials stored in Jenkins by sending a crafted webhook payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41937
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3165
- http://www.openwall.com/lists/oss-security/2023/09/06/9

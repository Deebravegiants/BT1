# [M] Jenkins Artifactory Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8q6r-5hc6-hrr8
CVE: CVE-2019-10321
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8q6r-5hc6-hrr8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:artifactory` — affected >=0

## Details
Jenkins Artifactory Plugin does not perform permission checks on a method implementing form validation. This allows users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery vulnerability.

As of publication of this advisory, no release containing a fix is available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10321
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1015%20(1)
- https://web.archive.org/web/20200227054747/http://www.securityfocus.com/bid/108540
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0787
- http://www.openwall.com/lists/oss-security/2019/05/31/2

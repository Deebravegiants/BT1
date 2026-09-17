# [M] Missing Authorization in Jenkins XP-Dev Plugin

## Summary
Severity: Medium
Advisory: GHSA-x9wp-gfrr-p5rp
CVE: CVE-2022-45389
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-x9wp-gfrr-p5rp
Type: github-advisory

## Affected
- Maven: `com.cloudbees.jenkins.plugins:xpdev` — affected >=0

## Details
A missing permission check in Jenkins XP-Dev Plugin 1.0 and earlier allows unauthenticated attackers to trigger builds of jobs corresponding to an attacker-specified repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45389
- https://github.com/jenkinsci/xpdev-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2853
- http://www.openwall.com/lists/oss-security/2022/11/15/4

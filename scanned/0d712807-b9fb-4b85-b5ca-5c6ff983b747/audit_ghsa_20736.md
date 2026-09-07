# [M] Cross-site Scripting in Jenkins Job Configuration History Plugin

## Summary
Severity: Medium
Advisory: GHSA-28w4-h56g-grg7
CVE: CVE-2022-38664
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-28w4-h56g-grg7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jobConfigHistory` — affected >=0 <1166.vc9f255f45b

## Details
Jenkins Job Configuration History Plugin 1165.v8cc9fd1f4597 and earlier does not escape the job name on the System Configuration History page, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure job names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38664
- https://github.com/jenkinsci/job-config-history-plugin/commit/c9f255f45b8a6ed008d66be094526adfd80ca035
- https://github.com/jenkinsci/job-config-history-plugin
- https://www.jenkins.io/security/advisory/2022-08-23/#SECURITY-2765
- http://www.openwall.com/lists/oss-security/2022/08/23/2

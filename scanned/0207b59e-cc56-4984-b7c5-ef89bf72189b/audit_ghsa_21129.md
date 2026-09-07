# [H] Cross-site Scripting in Jenkins Plot Plugin

## Summary
Severity: High
Advisory: GHSA-hpf7-mmqw-g6vq
CVE: CVE-2022-34783
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-hpf7-mmqw-g6vq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:plot` — affected >=0 <2.1.11

## Details
Jenkins Plot Plugin 2.1.10 and earlier does not escape plot descriptions, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34783
- https://github.com/jenkinsci/plot-plugin/commit/4b681af2888da49c41863ccc9f6eaa3ea26367d8
- https://github.com/jenkinsci/plot-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2220

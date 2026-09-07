# [M] Stored XSS vulnerability in Jenkins Maven Repository Server Plugin

## Summary
Severity: Medium
Advisory: GHSA-9pvw-8q92-hm9w
CVE: CVE-2023-35143
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-9pvw-8q92-hm9w
Type: github-advisory

## Affected
- Maven: `jenkins:repository` — affected >=0

## Details
Jenkins Maven Repository Server Plugin 1.10 and earlier does not escape the versions of build artifacts on the Build Artifacts As Maven Repository page, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control maven project versions in `pom.xml`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35143
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-3156
- http://www.openwall.com/lists/oss-security/2023/06/14/5

# [H] Jenkins JaCoCo Plugin vulnerable to Stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-xj29-gfww-j67g
CVE: CVE-2023-28669
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-xj29-gfww-j67g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jacoco` — affected >=0 <3.3.2.1

## Details
Jenkins JaCoCo Plugin 3.3.2 and earlier does not escape class and method names shown on the UI, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control input files for the 'Record JaCoCo coverage report' post-build action. Version 3.3.2.1 escapes class and method names shown on the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28669
- https://github.com/jenkinsci/jacoco-plugin/commit/96386f94b00e8802c4905b58e5c3dc4fa4a7c1cd
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-3061

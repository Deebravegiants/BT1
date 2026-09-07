# [M] Stored Cross-site Scripting vulnerability in Jenkins Promoted Builds (Simple) Plugin

## Summary
Severity: Medium
Advisory: GHSA-gc7q-7vg3-h8gf
CVE: CVE-2022-25202
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-gc7q-7vg3-h8gf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:promoted-builds-simple` — affected >=0

## Details
Jenkins Promoted Builds (Simple) Plugin 1.9 and earlier does not escape the name of custom promotion levels, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25202
- https://github.com/jenkinsci/promoted-builds-simple-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2334

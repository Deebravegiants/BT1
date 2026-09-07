# [H] XXE vulnerability in Jenkins JAPEX Plugin

## Summary
Severity: High
Advisory: GHSA-8538-25v4-25pg
CVE: CVE-2022-45400
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-8538-25v4-25pg
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:japex` — affected >=0

## Details
JAPEX Plugin 1.7 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control XML input files for the 'Record Japex test report' post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45400
- https://github.com/jenkinsci/japex-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2941
- http://www.openwall.com/lists/oss-security/2022/11/15/4

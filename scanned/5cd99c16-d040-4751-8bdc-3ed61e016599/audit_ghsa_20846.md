# [M] Jenkins RQM Plugin vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: Medium
Advisory: GHSA-j8xr-2279-88qj
CVE: CVE-2022-41241
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-j8xr-2279-88qj
Type: github-advisory

## Affected
- Maven: `net.praqma:rqm-plugin` — affected >=0

## Details
Jenkins RQM Plugin 2.8 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks. This allows attackers able to provide crafted API responses from Rational Quality Manager to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery. There is currently no known workaround or fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41241
- https://github.com/jenkinsci/rqm-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2805

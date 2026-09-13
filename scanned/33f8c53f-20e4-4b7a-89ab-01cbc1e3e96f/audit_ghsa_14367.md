# [H] Jenkins remote-jobs-view-plugin vulnerable to XML external entity attacks

## Summary
Severity: High
Advisory: GHSA-58ch-c2jf-5g23
CVE: CVE-2023-28684
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-58ch-c2jf-5g23
Type: github-advisory

## Affected
- Maven: `com.sap.jenkinsci:remote-jobs-view-plugin` — affected >=0

## Details
Jenkins remote-jobs-view-plugin Plugin 0.0.3 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows authenticated attackers with Overall/Read permission to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28684
- https://github.com/jenkinsci/remote-jobs-view-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2956

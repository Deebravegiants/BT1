# [M] CSRF vulnerability in Jenkins Job and Node ownership Plugin

## Summary
Severity: Medium
Advisory: GHSA-9hcj-449v-9234
CVE: CVE-2022-28152
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-9hcj-449v-9234
Type: github-advisory

## Affected
- Maven: `com.synopsys.jenkinsci:ownership` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Job and Node ownership Plugin 0.13.0 and earlier allows attackers to restore the default ownership of a job.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28152
- https://github.com/jenkinsci/ownership-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2062%20(2)
- http://www.openwall.com/lists/oss-security/2022/03/29/1

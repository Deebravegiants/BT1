# [H] Stored Cross-site Scripting vulnerability in Jenkins Job and Node ownership Plugin

## Summary
Severity: High
Advisory: GHSA-x63v-prhc-xx6f
CVE: CVE-2022-28149
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-x63v-prhc-xx6f
Type: github-advisory

## Affected
- Maven: `com.synopsys.jenkinsci:ownership` — affected >=0

## Details
Jenkins Job and Node ownership Plugin 0.13.0 and earlier does not escape the names of the secondary owners, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28149
- https://github.com/jenkinsci/ownership-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2285
- http://www.openwall.com/lists/oss-security/2022/03/29/1

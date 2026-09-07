# [H] Jenkins Matrix Reloaded Plugin vulnerable to Stored XSS

## Summary
Severity: High
Advisory: GHSA-2463-7265-h8r4
CVE: CVE-2022-34788
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-2463-7265-h8r4
Type: github-advisory

## Affected
- Maven: `net.praqma:matrix-reloaded` — affected >=0

## Details
Jenkins Matrix Reloaded Plugin 1.1.3 and earlier does not escape the agent name in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Agent/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34788
- https://github.com/jenkinsci/matrix-reloaded-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1926

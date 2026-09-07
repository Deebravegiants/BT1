# [H] Jenkins Quay.io trigger Plugin Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-2jgw-28qh-6mg8
CVE: CVE-2023-30520
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-2jgw-28qh-6mg8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:quayio-trigger` — affected >=0

## Details
Jenkins Quay.io trigger Plugin 0.1 and earlier does not limit URL schemes for repository homepage URLs submitted via Quay.io trigger webhooks. This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to submit crafted Quay.io trigger webhook payloads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30520
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2850
- http://www.openwall.com/lists/oss-security/2023/04/13/3

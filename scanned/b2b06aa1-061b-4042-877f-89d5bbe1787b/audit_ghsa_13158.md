# [H] Disabled permissions can be granted by Jenkins SSH2 Easy Plugin

## Summary
Severity: High
Advisory: GHSA-4gh2-m88h-8cj8
CVE: CVE-2023-41939
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-4gh2-m88h-8cj8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ssh2easy` — affected >=0 <1.6

## Details
Jenkins SSH2 Easy Plugin 1.4 and earlier does not verify that permissions configured to be granted are enabled, potentially allowing users formerly granted (typically optional permissions, like Overall/Manage) to access functionality they're no longer entitled to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41939
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3064
- http://www.openwall.com/lists/oss-security/2023/09/06/9

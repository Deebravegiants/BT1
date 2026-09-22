# [M] Jenkins Google Compute Engine Plugin does not verify SSH host keys when connecting agents created by the plugin

## Summary
Severity: Medium
Advisory: GHSA-345p-pw5q-g98v
CVE: CVE-2019-16546
CWE: CWE-300, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-345p-pw5q-g98v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=0 <4.2.0

## Details
Jenkins Google Compute Engine Plugin 4.1.1 and earlier does not verify SSH host keys when connecting agents created by the plugin, enabling man-in-the-middle attacks. Google Compute Engine Plugin 4.2.0 verifies SSH host keys before executing any commands on agents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16546
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1584
- http://www.openwall.com/lists/oss-security/2019/11/21/1

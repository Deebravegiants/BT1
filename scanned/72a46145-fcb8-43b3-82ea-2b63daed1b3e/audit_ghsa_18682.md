# [H] Jenkins Azure CLI Plugin does not restrict the commands it executes

## Summary
Severity: High
Advisory: GHSA-rh72-238f-g26q
CVE: CVE-2025-64140
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-rh72-238f-g26q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-cli` — affected >=0

## Details
Jenkins Azure CLI Plugin 0.9 and earlier does not restrict which commands it executes on the Jenkins controller.

This allows attackers with Item/Configure permission to execute arbitrary shell commands on the Jenkins controller.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64140
- https://github.com/jenkinsci/azure-cli-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3538
- http://www.openwall.com/lists/oss-security/2025/10/29/2

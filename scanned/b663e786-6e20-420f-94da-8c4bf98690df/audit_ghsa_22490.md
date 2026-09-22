# [M] Missing permission check in Jenkins Blue Ocean Plugin

## Summary
Severity: Medium
Advisory: GHSA-5m4q-x28v-q6wp
CVE: CVE-2022-30954
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-5m4q-x28v-q6wp
Type: github-advisory

## Affected
- Maven: `io.jenkins.blueocean:blueocean-parent` — affected >=0 <1.25.4

## Details
Jenkins Blue Ocean Plugin 1.25.3 and earlier does not perform a permission check in several HTTP endpoints, allowing attackers with Overall/Read permission to connect to an attacker-specified HTTP server. Blue Ocean Plugin 1.25.4 requires POST requests and the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30954
- https://github.com/jenkinsci/blueocean-plugin/commit/ffd89b675b172c86613459935fe220dc2bba0c57
- https://github.com/jenkinsci/blueocean-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2502
- http://www.openwall.com/lists/oss-security/2022/05/17/8

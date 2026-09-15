# [M] Jenkins Filesystem List Parameter Plugin has Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fwxq-3f52-5cmc
CVE: CVE-2024-54004
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-fwxq-3f52-5cmc
Type: github-advisory

## Affected
- Maven: `aendter.jenkins.plugins:filesystem-list-parameter-plugin` — affected >=0 <0.0.15

## Details
Jenkins Filesystem List Parameter Plugin 0.0.14 and earlier does not restrict the path used for the File system objects list Parameter.

This allows attackers with Item/Configure permission to enumerate file names on the Jenkins controller file system.

Filesystem List Parameter Plugin 0.0.15 ensures that paths used by the File system objects list Parameter are restricted to an allow list, with the default base directory set to $JENKINS_HOME/userContent/. The allow list can be configured to include additional custom base directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54004
- https://www.jenkins.io/security/advisory/2024-11-27/#SECURITY-3367

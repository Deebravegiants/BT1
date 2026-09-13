# [M] Jenkins Compuware Source Code Download is missing authorization

## Summary
Severity: Medium
Advisory: GHSA-75fc-fv3p-xh82
CVE: CVE-2022-36896
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-75fc-fv3p-xh82
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-scm-downloader` — affected >=0 <2.0.13

## Details
BMC Compuware Source Code Download for Endevor, PDS, and ISPW Plugin 2.0.12 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate hosts and ports of Compuware configurations and credentials IDs of credentials stored in Jenkins. Those credentials IDs can be used as part of an attack to capture the credentials using another vulnerability.

BMC Compuware Source Code Download for Endevor, PDS, and ISPW Plugin 2.0.13 requires the appropriate permissions to enumerate hosts and ports of Compuware configurations and credentials IDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36896
- https://github.com/jenkinsci/compuware-scm-downloader-plugin/commit/bf00665b13641351a9f67027bbe34609cc4f65e2
- https://github.com/jenkinsci/compuware-scm-downloader-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2621
- http://www.openwall.com/lists/oss-security/2022/07/27/1

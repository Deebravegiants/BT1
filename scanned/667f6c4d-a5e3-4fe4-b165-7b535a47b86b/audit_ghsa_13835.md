# [M] Synopsys Jenkins Coverity Plugin has Incorrect Default Permissions

## Summary
Severity: Medium
Advisory: GHSA-jwr6-75xh-jh5j
CVE: CVE-2023-23850
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-jwr6-75xh-jh5j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:synopsys-coverity` — affected >=0 <3.0.3

## Details
Synopsys Coverity Plugin 3.0.2 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Synopsys Coverity Plugin 3.0.3 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-23850
- https://community.synopsys.com/s/article/SIG-Product-Security-Advisory-Multiple-CVEs-affecting-Coverity-Jenkins-Plugin
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-2793%20(1)

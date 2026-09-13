# [M] Jenkins Compuware Xpediter Code Coverage Plugin Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-hxf7-9rv9-88v6
CVE: CVE-2022-36897
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-hxf7-9rv9-88v6
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-xpediter-code-coverage` — affected >=0 <1.0.8

## Details
Jenkins Compuware Xpediter Code Coverage Plugin 1.0.7 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate hosts and ports of Compuware configurations and credentials IDs of credentials stored in Jenkins. Those credentials IDs can be used as part of an attack to capture the credentials using another vulnerability.

Compuware Xpediter Code Coverage Plugin 1.0.8 requires the appropriate permissions to enumerate hosts and ports of Compuware configurations and credentials IDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36897
- https://github.com/jenkinsci/compuware-xpediter-code-coverage-plugin/commit/2bb312d91f8dc20e7e1e2098584dbea65a9bffb6
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2626
- http://www.openwall.com/lists/oss-security/2022/07/27/1

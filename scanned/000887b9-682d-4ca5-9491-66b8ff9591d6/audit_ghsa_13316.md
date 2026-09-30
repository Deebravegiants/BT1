# [M] Jenkins mabl Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-23rr-6phq-5p65
CVE: CVE-2023-37950
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-23rr-6phq-5p65
Type: github-advisory

## Affected
- Maven: `com.mabl.integration.jenkins:mabl-integration` — affected >=0 <0.0.47

## Details
Jenkins mabl Plugin 0.0.46 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in mabl Plugin 0.0.47 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37950
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3137%20(1)
- http://www.openwall.com/lists/oss-security/2023/07/12/2

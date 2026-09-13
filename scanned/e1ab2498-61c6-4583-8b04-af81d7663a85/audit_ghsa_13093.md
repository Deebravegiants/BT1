# [M] Jenkins Delphix Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-3fqw-j7x8-g75j
CVE: CVE-2023-40344
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-3fqw-j7x8-g75j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:delphix` — affected >=0 <3.0.3

## Details
Jenkins Delphix Plugin 3.0.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Delphix Plugin 3.0.3 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40344
- https://support.delphix.com/Support_Policies_and_Technical_Bulletins/Technical_Bulletins/TB111_Delphix_Plugin_for_Jenkins_Vulnerable_to_Credential_Enumeration_and_Capture
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3214%20(1)
- http://www.openwall.com/lists/oss-security/2023/08/16/3

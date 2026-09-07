# [M] Jenkins OctoPerf Load Testing Plugin missing permission check allows for ID enumeration 

## Summary
Severity: Medium
Advisory: GHSA-mjg3-2v66-p34j
CVE: CVE-2023-28673
CWE: CWE-284, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-mjg3-2v66-p34j
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:octoperf` — affected >=0 <4.5.3

## Details
OctoPerf Load Testing Plugin Plugin 4.5.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in OctoPerf Load Testing Plugin Plugin 4.5.3 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28673
- https://github.com/jenkinsci/octoperf-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-3067%20(3)

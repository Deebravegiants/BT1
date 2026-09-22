# [M] Jenkins Oracle Cloud Infrastructure Compute Plugin missing SSH host key validation

## Summary
Severity: Medium
Advisory: GHSA-j54r-w587-95q7
CVE: CVE-2023-37948
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-j54r-w587-95q7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oracle-cloud-infrastructure-compute` — affected >=0 <1.0.17

## Details
Jenkins Oracle Cloud Infrastructure Compute Plugin 1.0.16 and earlier does not perform SSH host key validation when connecting to OCI clouds.

This lack of validation could be abused using a man-in-the-middle attack to intercept these connections to OCI clouds.

Oracle Cloud Infrastructure Compute Plugin 1.0.17 provides strategies for performing host key validation for administrators to select the one that meets their security needs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37948
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3044
- http://www.openwall.com/lists/oss-security/2023/07/12/2

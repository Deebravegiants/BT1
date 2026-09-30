# [M] Jenkins Compuware ISPW Operations Plugin does not perform permission checks in several HTTP endpoints

## Summary
Severity: Medium
Advisory: GHSA-cp5r-xqjr-84gm
CVE: CVE-2022-36898
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-cp5r-xqjr-84gm
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-ispw-operations` — affected >=0 <1.0.9

## Details
Jenkins BMC AMI DevX Code Pipeline Operations Plugin 1.0.8 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate hosts and ports of Compuware configurations and credentials IDs of credentials stored in Jenkins. Those credentials IDs can be used as part of an attack to capture the credentials using another vulnerability.

BMC AMI DevX Code Pipeline Operations Plugin 1.0.9 requires the appropriate permissions to enumerate hosts and ports of Compuware configurations and credentials IDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36898
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2628
- http://www.openwall.com/lists/oss-security/2022/07/27/1

# [M] Jenkins Compuware Topaz Utilities Plugin is missing authorization

## Summary
Severity: Medium
Advisory: GHSA-qf4p-7gqc-x6jx
CVE: CVE-2022-36895
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-qf4p-7gqc-x6jx
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-utilities` — affected >=0 <1.0.9

## Details
Jenkins Compuware Topaz Utilities Plugin 1.0.8 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate hosts and ports of Compuware configurations and credentials IDs of credentials stored in Jenkins. Those credentials IDs can be used as part of an attack to capture the credentials using another vulnerability.

Compuware Topaz Utilities Plugin 1.0.9 requires the appropriate permissions to enumerate hosts and ports of Compuware configurations and credentials IDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36895
- https://github.com/jenkinsci/compuware-topaz-utilities-plugin/commit/a79f95c7d32ad6a2e161159fa77f371705f3b20d
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2619
- http://www.openwall.com/lists/oss-security/2022/07/27/1

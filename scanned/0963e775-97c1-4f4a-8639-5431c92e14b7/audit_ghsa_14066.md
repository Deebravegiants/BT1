# [M] Jenkins Azure VM Agents Plugin missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-rv6g-3v76-cvf9
CVE: CVE-2023-32990
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-rv6g-3v76-cvf9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-vm-agents` — affected >=0 <853.v4a

## Details
Jenkins Azure VM Agents Plugin 852.v8d35f0960a_43 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified Azure Cloud server using attacker-specified credentials IDs obtained through another method.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Azure VM Agents Plugin 853.v4a_1a_dd947520 requires POST requests and the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32990
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2855%20(2)

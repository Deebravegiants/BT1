# [M] Jenkins Google Compute Engine Plugin has incorrect permission checks

## Summary
Severity: Medium
Advisory: GHSA-pgpj-83g3-mfr2
CVE: CVE-2023-49652
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-pgpj-83g3-mfr2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=0 <4.3.17.1
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=4.5 <4.551.v5a

## Details
Jenkins Google Compute Engine Plugin 4.550.vb_327fca_3db_11 and earlier does not correctly perform permission checks in multiple HTTP endpoints. This allows attackers with global Item/Configure permission (while lacking Item/Configure permission on any particular job) to do the following:

- Enumerate system-scoped credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

- Connect to Google Cloud Platform using attacker-specified credentials IDs obtained through another method, to obtain information about existing projects.

Google Compute Engine Plugin 4.551.v5a_4dc98f6962 requires Overall/Administer permission for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49652
- https://www.jenkins.io/security/advisory/2023-11-29/#SECURITY-2835
- http://www.openwall.com/lists/oss-security/2023/11/29/1

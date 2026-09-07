# [M] Jenkins HashiCorp Vault Plugin does not perform permission checks in several HTTP endpoints that perform Vault connection tests

## Summary
Severity: Medium
Advisory: GHSA-vpf7-q2rx-26mh
CVE: CVE-2022-36888
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-vpf7-q2rx-26mh
Type: github-advisory

## Affected
- Maven: `com.datapipe.jenkins.plugins:hashicorp-vault-plugin` — affected >=0 <355.v3b_38d767a_b_a_8

## Details
A missing permission check in Jenkins HashiCorp Vault Plugin 354.vdb_858fd6b_f48 and earlier allows attackers with Overall/Read permission to obtain credentials stored in Vault with attacker-specified path and keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36888
- https://github.com/jenkinsci/hashicorp-vault-plugin/commit/3b38d767aba8bd98d6f4fb53c1f1678d95b5e752
- https://github.com/jenkinsci/hashicorp-vault-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2593
- http://www.openwall.com/lists/oss-security/2022/07/27/1

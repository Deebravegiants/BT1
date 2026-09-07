# [C] HashiCorp Vault vulnerable to incorrect metadata access

## Summary
Severity: Critical
Advisory: GHSA-7cgv-v83v-rr87
CVE: CVE-2022-40186
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-7cgv-v83v-rr87
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.11.0 <1.11.3
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.10.6
- Go: `github.com/hashicorp/vault` — affected >=1.8.0 <1.9.9

## Details
An issue was discovered in HashiCorp Vault and Vault Enterprise before 1.11.3. A vulnerability in the Identity Engine was found where, in a deployment where an entity has multiple mount accessors with shared alias names, Vault may overwrite metadata to the wrong alias due to an issue with checking the proper alias assigned to an entity. This may allow for unintended access to key/value paths using that metadata in Vault.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40186
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-18-vault-entity-alias-metadata-may-leak-between-aliases-with-the-same-name-assigned-to-the-same-entity/44550
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20221111-0008

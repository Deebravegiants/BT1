# [C] HashiCorp Vault underlying database had excessively broad filesystem permissions from v1.4.0 until v1.8.0

## Summary
Severity: Critical
Advisory: GHSA-23fq-q7hc-993r
CVE: CVE-2021-38553
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-23fq-q7hc-993r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.4.0 <1.8.0

## Details
HashiCorp Vault and Vault Enterprise 1.4.0 through 1.7.3 initialized an underlying database file associated with the Integrated Storage feature with excessively broad filesystem permissions. Fixed in Vault and Vault Enterprise 1.8.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38553
- https://discuss.hashicorp.com/t/hcsec-2021-20-vault-s-integrated-storage-backend-database-file-may-have-excessively-broad-permissions/28168
- https://github.com/hashicorp/vault
- https://security.gentoo.org/glsa/202207-01

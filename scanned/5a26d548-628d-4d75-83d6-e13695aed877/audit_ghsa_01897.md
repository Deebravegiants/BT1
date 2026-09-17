# [C] HashiCorp Vault Incorrect Permission Assignment for Critical Resource

## Summary
Severity: Critical
Advisory: GHSA-pfmw-vj74-ph8g
CVE: CVE-2021-43998
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-pfmw-vj74-ph8g
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.11.0 <1.7.6
- Go: `github.com/hashicorp/vault` — affected >=1.8.0 <1.8.5

## Details
HashiCorp Vault and Vault Enterprise 0.11.0 up to 1.7.5 and 1.8.4 templated ACL policies would always match the first-created entity alias if multiple entity aliases exist for a specified entity and mount combination, potentially resulting in incorrect policy enforcement. Fixed in Vault and Vault Enterprise 1.7.6, 1.8.5, and 1.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43998
- https://discuss.hashicorp.com/t/hcsec-2021-30-vaults-templated-acl-policies-matched-first-created-alias-per-entity-and-auth-backend/32132
- https://github.com/hashicorp/vault
- https://security.gentoo.org/glsa/202207-01

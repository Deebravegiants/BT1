# [H] Hashicorp Vault Fails to Verify if Approle SecretID Belongs to Role During a Destroy Operation

## Summary
Severity: High
Advisory: GHSA-wmg5-g953-qqfw
CVE: CVE-2023-24999
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-wmg5-g953-qqfw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.10.11
- Go: `github.com/hashicorp/vault` — affected >=1.11.0 <1.11.8
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.12.4

## Details
When using the Vault and Vault Enterprise (Vault) approle auth method, any authenticated user with access to the `/auth/approle/role/:role_name/secret-id-accessor/destroy` endpoint can destroy the secret ID of any other role by providing the secret ID accessor. This vulnerability, CVE-2023-24999, has been fixed in Vault 1.13.0, 1.12.4, 1.11.8, 1.10.11 and above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24999
- https://discuss.hashicorp.com/t/hcsec-2023-07-vault-fails-to-verify-if-approle-secretid-belongs-to-role-during-a-destroy-operation/51305
- https://github.com/hashicorp/vault

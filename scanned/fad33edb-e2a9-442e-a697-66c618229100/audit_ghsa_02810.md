# [H] Incorrect Privilege Assignment in HashiCorp Vault

## Summary
Severity: High
Advisory: GHSA-362v-wg5p-64w2
CVE: CVE-2021-42135
CWE: CWE-266, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-362v-wg5p-64w2
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.8.0

## Details
HashiCorp Vault and Vault Enterprise 1.8.x through 1.8.4 may have an unexpected interaction between glob-related policies and the Google Cloud secrets engine. Users may, in some situations, have more privileges than intended, e.g., a user with read permission for the /gcp/roleset/* path may be able to issue Google Cloud service account credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42135
- https://discuss.hashicorp.com/t/hcsec-2021-28-vaults-google-cloud-secrets-engine-policies-with-globs-may-provide-additional-privileges-in-vault-1-8-0-onwards
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/blob/main/CHANGELOG.md#180

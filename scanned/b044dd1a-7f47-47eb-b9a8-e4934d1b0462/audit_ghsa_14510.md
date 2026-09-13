# [M] HashiCorp Vault's PKI mount vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-hwc3-3qh6-r4gg
CVE: CVE-2023-0665
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-hwc3-3qh6-r4gg
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.11.9
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.12.5
- Go: `github.com/hashicorp/vault` — affected >=1.13.0 <1.13.1

## Details
HashiCorp Vault's PKI mount issuer endpoints did not correctly authorize access to remove an issuer or modify issuer metadata, potentially resulting in denial of service of the PKI mount. This bug did not affect public or private key material, trust chains or certificate issuance. Fixed in Vault 1.13.1, 1.12.5, and 1.11.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0665
- https://discuss.hashicorp.com/t/hcsec-2023-11-vault-s-pki-issuer-endpoint-did-not-correctly-authorize-access-to-issuer-metadata/52079/1
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20230526-0008

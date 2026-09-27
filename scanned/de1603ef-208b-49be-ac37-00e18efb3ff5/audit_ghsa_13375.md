# [M] HashiCorp Vault's revocation list not respected

## Summary
Severity: Medium
Advisory: GHSA-9mh8-9j64-443f
CVE: CVE-2022-41316
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-9mh8-9j64-443f
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.11.0 <1.11.4
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.10.7
- Go: `github.com/hashicorp/vault` — affected >=0 <1.9.10

## Details
HashiCorp Vault and Vault Enterprise’s TLS certificate auth method did not initially load the optionally configured CRL issued by the role's CA into memory on startup, resulting in the revocation list not being checked if the CRL has not yet been retrieved. Fixed in 1.12.0, 1.11.4, 1.10.7, and 1.9.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41316
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-24-vaults-tls-cert-auth-method-only-loaded-crl-after-first-request/45483
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20221201-0001

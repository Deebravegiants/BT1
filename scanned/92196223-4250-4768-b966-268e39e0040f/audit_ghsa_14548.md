# [M] HashiCorp Vault's implementation of Shamir's secret sharing vulnerable to cache-timing attacks

## Summary
Severity: Medium
Advisory: GHSA-vq4h-9ghm-qmrr
CVE: CVE-2023-25000
CWE: CWE-203, CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-vq4h-9ghm-qmrr
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.11.9
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.12.5
- Go: `github.com/hashicorp/vault` — affected >=1.13.0 <1.13.1

## Details
HashiCorp Vault's implementation of Shamir's secret sharing used precomputed table lookups, and was vulnerable to cache-timing attacks. An attacker with access to, and the ability to observe a large number of unseal operations on the host through a side channel may reduce the search space of a brute force effort to recover the Shamir shares. Fixed in Vault 1.13.1, 1.12.5, and 1.11.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25000
- https://github.com/hashicorp/vault/pull/19495
- https://discuss.hashicorp.com/t/hcsec-2023-10-vault-vulnerable-to-cache-timing-attacks-during-seal-and-unseal-operations/52078
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20230526-0008

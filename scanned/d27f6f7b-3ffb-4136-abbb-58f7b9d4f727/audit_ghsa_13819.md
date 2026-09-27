# [H] HashiCorp Vault Missing Release of Memory after Effective Lifetime vulnerability

## Summary
Severity: High
Advisory: GHSA-4qhc-v8r6-8vwm
CVE: CVE-2023-5954
CWE: CWE-401
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-09
Source: https://github.com/advisories/GHSA-4qhc-v8r6-8vwm
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.13.10
- Go: `github.com/hashicorp/vault` — affected >=1.14.0 <1.14.6
- Go: `github.com/hashicorp/vault` — affected >=1.15.0 <1.15.2

## Details
HashiCorp Vault and Vault Enterprise inbound client requests triggering a policy check can lead to an unbounded consumption of memory. A large number of these requests may lead to denial-of-service. Fixed in Vault 1.15.2, 1.14.6, and 1.13.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5954
- https://discuss.hashicorp.com/t/hcsec-2023-33-vault-requests-triggering-policy-checks-may-lead-to-unbounded-memory-consumption/59926
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20231227-0001

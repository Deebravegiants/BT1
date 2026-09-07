# [M] HashiCorp Vault improper configuration of multi factor authentication

## Summary
Severity: Medium
Advisory: GHSA-c5wc-v287-82pc
CVE: CVE-2022-30689
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-c5wc-v287-82pc
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.10.3

## Details
HashiCorp Vault and Vault Enterprise from 1.10.0 to 1.10.2 did not correctly configure and enforce MFA on login after server restarts. This affects the Login MFA feature introduced in Vault and Vault Enterprise 1.10.0 and does not affect the separate Enterprise MFA feature set. Fixed in 1.10.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30689
- https://github.com/hashicorp/vault/commit/15baea5fa3e71c837c33b8bcbd8f06e0fbbc110d
- https://discuss.hashicorp.com
- https://github.com/hashicorp/vault
- https://security.gentoo.org/glsa/202207-01
- https://security.netapp.com/advisory/ntap-20220629-0006

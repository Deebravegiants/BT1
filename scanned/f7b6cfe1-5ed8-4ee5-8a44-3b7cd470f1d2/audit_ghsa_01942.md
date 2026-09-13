# [H] Invalid session token expiration 

## Summary
Severity: High
Advisory: GHSA-38j9-7pp9-2hjw
CVE: CVE-2021-32923
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-38j9-7pp9-2hjw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.7.0 <1.7.2
- Go: `github.com/hashicorp/vault` — affected >=1.6.0 <1.6.5
- Go: `github.com/hashicorp/vault` — affected >=0.10.0 <1.5.9

## Details
HashiCorp Vault and Vault Enterprise allowed the renewal of nearly-expired token leases and dynamic secret leases (specifically, those within 1 second of their maximum TTL), which caused them to be incorrectly treated as non-expiring during subsequent use. Fixed in 1.5.9, 1.6.5, and 1.7.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32923
- https://discuss.hashicorp.com/t/hcsec-2021-15-vault-renewed-nearly-expired-leases-with-incorrect-non-expiring-ttls/24603
- https://security.gentoo.org/glsa/202207-01
- https://www.hashicorp.com/blog/category/vault

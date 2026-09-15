# [H] Improper Authentication in HashiCorp Vault

## Summary
Severity: High
Advisory: GHSA-rq95-xf66-j689
CVE: CVE-2021-3282
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-rq95-xf66-j689
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.6.0 <1.6.2

## Details
HashiCorp Vault Enterprise 1.6.0 & 1.6.1 allowed the `remove-peer` raft operator command to be executed against DR secondaries without authentication. Fixed in 1.6.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3282
- https://github.com/hashicorp/vault/commit/09f9068e22f762da123160233518b440e00bdb3b
- https://discuss.hashicorp.com/t/hcsec-2021-04-vault-enterprise-s-dr-secondaries-allowed-raft-peer-removal-without-authentication/20337
- https://security.gentoo.org/glsa/202207-01

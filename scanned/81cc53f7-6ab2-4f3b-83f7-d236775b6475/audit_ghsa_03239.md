# [H] Information Disclosure in HashiCorp Vault

## Summary
Severity: High
Advisory: GHSA-25xj-89g5-fm6h
CVE: CVE-2020-13223
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-25xj-89g5-fm6h
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.3.0 <1.3.6
- Go: `github.com/hashicorp/vault` — affected >=1.4.0 <1.4.2

## Details
HashiCorp Vault and Vault Enterprise before 1.3.6, and 1.4.2 before 1.4.2, insert Sensitive Information into a Log File. The vulnerability is affecting `github.com/hashicorp/vault/command` Go package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13223
- https://github.com/hashicorp/vault/commit/87f47c216cf1a28f4054b80cff40de8c9e00e36c
- https://github.com/hashicorp/vault/commit/e52f34772affb69f3239b2cdf6523cb7cfd67a92
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#142-may-21st-2020
- https://www.hashicorp.com/blog/category/vault

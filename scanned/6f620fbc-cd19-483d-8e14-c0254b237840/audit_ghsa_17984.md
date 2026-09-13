# [H] HashiCorp go-getter Vulnerable to Symlink Attacks

## Summary
Severity: High
Advisory: GHSA-wjrx-6529-hcj3
CVE: CVE-2025-8959
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-15
Source: https://github.com/advisories/GHSA-wjrx-6529-hcj3
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=0 <1.7.9

## Details
HashiCorp's go-getter library subdirectory download feature is vulnerable to symlink attacks leading to unauthorized read access beyond the designated directory boundaries. This vulnerability, identified as CVE-2025-8959, is fixed in go-getter 1.7.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8959
- https://github.com/hashicorp/go-getter/commit/87541b2501c00df5eaedea6acc61a2a4a4efa5b7
- https://discuss.hashicorp.com/t/hcsec-2025-23-hashicorp-go-getter-vulnerable-to-arbitrary-read-through-symlink-attack/76242
- https://github.com/hashicorp/go-getter
- https://pkg.go.dev/vuln/GO-2025-3892

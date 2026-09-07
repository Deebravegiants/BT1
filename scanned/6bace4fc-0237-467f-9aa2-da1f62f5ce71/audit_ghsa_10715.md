# [H] HashiCorp's go-getter library may allow arbitrary file reads

## Summary
Severity: High
Advisory: GHSA-92mm-2pjq-r785
CVE: CVE-2026-4660
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-92mm-2pjq-r785
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=0 <1.8.6

## Details
HashiCorp's go-getter library up to v1.8.5 may allow arbitrary file reads on the file system during certain git operations through a maliciously crafted URL. This is fixed in go-getter v1.8.6. This vulnerability does not affect the go-getter/v2 branch and package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4660
- https://discuss.hashicorp.com/t/hcsec-2026-04-go-getter-may-allow-to-arbitrary-filesystem-reads-through-git-operations/77311
- https://github.com/hashicorp/go-getter

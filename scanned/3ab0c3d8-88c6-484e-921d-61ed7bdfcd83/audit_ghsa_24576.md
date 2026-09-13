# [H] Arbitrary file deletion in gitea

## Summary
Severity: High
Advisory: GHSA-g7p7-x6w7-w6qg
CVE: CVE-2022-27313
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-g7p7-x6w7-w6qg
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.16.4

## Details
An arbitrary file deletion vulnerability in Gitea v1.16.3 allows attackers to cause a Denial of Service (DoS) via deleting the configuration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27313
- https://github.com/go-gitea/gitea/pull/19072
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.16.4

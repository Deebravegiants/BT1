# [H] Denial of Service in Gitea

## Summary
Severity: High
Advisory: GHSA-g2qx-6ghw-67hm
CVE: CVE-2020-13246
CWE: CWE-667
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g2qx-6ghw-67hm
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.12.0

## Details
An issue was discovered in Gitea in which an attacker can trigger a deadlock by initiating a transfer of a repository's ownership from one organization to another.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13246
- https://github.com/go-gitea/gitea/issues/10549
- https://github.com/go-gitea/gitea/pull/11438
- https://www.youtube.com/watch?v=DmVgADSVS88

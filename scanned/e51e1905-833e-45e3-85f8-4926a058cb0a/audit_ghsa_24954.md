# [H] Gogs and Gitea SSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-fg3x-rwq9-74cw
CVE: CVE-2018-15192
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fg3x-rwq9-74cw
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.16.0-rc1
- Go: `gogs.io/gogs` — affected >=0 <0.12.0

## Details
An SSRF vulnerability in webhooks in Gitea through 1.5.0-rc2 and Gogs through 0.11.53 allows remote attackers to access intranet services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15192
- https://github.com/go-gitea/gitea/issues/4624
- https://github.com/gogs/gogs/issues/5366
- https://github.com/go-gitea/gitea/pull/17482
- https://github.com/gogs/gogs/pull/6002
- https://github.com/go-gitea/gitea/commit/599ff1c054e436daa4dc3f049aa8661d9c2395f9
- https://github.com/gogs/gogs/commit/22717a1c064511cf37c46af5e650baf7184cf25b

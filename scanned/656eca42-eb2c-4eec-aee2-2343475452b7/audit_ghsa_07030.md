# [M] Gitea tracked-time deletion is not scoped to the requested issue

## Summary
Severity: Medium
Advisory: GHSA-qm72-8prh-g92x
CVE: CVE-2026-25782
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-qm72-8prh-g92x
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 look up tracked-time entries by time ID without scoping the lookup to the issue in the request URL, allowing deletion attempts to target entries from another issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25782
- https://github.com/go-gitea/gitea/pull/36664
- https://github.com/go-gitea/gitea/pull/36689
- https://github.com/go-gitea/gitea/commit/5ad87616c9c654fc44c611ccfd4e496257c8f96b
- https://github.com/go-gitea/gitea/commit/8051056075719b7629eef44689b5a61d5ff080a9
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5

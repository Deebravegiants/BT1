# [C] Gitea pre-receive hook scanner errors allow branch-protection bypass

## Summary
Severity: Critical
Advisory: GHSA-vhq7-fwwh-7hjf
CVE: CVE-2026-27780
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-vhq7-fwwh-7hjf
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.0

## Details
Gitea versions before 1.26.0 do not fail closed on bufio.Scanner errors while processing pre-receive hook input, allowing oversized input to bypass branch-protection checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27780
- https://github.com/go-gitea/gitea/pull/36963
- https://github.com/go-gitea/gitea/commit/c453d09c36fad094405314dba2f370434b200711
- https://blog.gitea.com/release-of-1.26.0
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.0

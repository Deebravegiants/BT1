# [H] Gitea has insufficient permission checks for Composer package source links

## Summary
Severity: High
Advisory: GHSA-8qw8-rq86-9pc2
CVE: CVE-2026-27771
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-8qw8-rq86-9pc2
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
### CVE Description
Gitea versions up to and including 1.26.1 have insufficient permission checks for Composer package source links, which can expose private or internal package source information.

### Summary
A critical vulnerability has been discovered in Gitea. It was already reported via (security@gitea.io) from (dev@noscope.com), and submitted an encrypted report.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-8qw8-rq86-9pc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27771
- https://github.com/go-gitea/gitea/pull/37610
- https://blog.gitea.com/release-of-1.26.2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.2

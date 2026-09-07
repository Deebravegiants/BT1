# [M] Gitea displaying raw OpenID error in UI

## Summary
Severity: Medium
Advisory: GHSA-8h8p-x289-vvqr
CVE: CVE-2021-45325
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-8h8p-x289-vvqr
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.7.0

## Details
Gitea is a project to help users set up a self-hosted Git service. Server Side Request Forgery (SSRF) vulnerability exists in Gitea before 1.7.0 using the OpenID URL. Gitea can leak sensitive information about the local network through the error provided by the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45325
- https://github.com/go-gitea/gitea/issues/4973
- https://github.com/go-gitea/gitea/pull/5705
- https://github.com/go-gitea/gitea/pull/5712
- https://blog.gitea.io/2019/01/gitea-1.7.0-is-released
- https://github.com/go-gitea/gitea

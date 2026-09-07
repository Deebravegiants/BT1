# [H] Cross Site Request Forgery in Gitea

## Summary
Severity: High
Advisory: GHSA-4wp3-8q92-mh8w
CVE: CVE-2021-45326
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-4wp3-8q92-mh8w
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.5.2

## Details
Cross Site Request Forgery (CSRF) vulnerability exists in Gitea before 1.5.2 via API routes.This can be dangerous especially with state altering POST requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45326
- https://github.com/go-gitea/gitea/issues/4838
- https://github.com/go-gitea/gitea/pull/4840
- https://blog.gitea.io/2018/10/gitea-1.5.2-is-released
- https://github.com/go-gitea/gitea

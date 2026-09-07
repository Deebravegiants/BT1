# [M] Cross-site Scripting in Gitea

## Summary
Severity: Medium
Advisory: GHSA-r3gq-wxqf-q4gh
CVE: CVE-2021-45329
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-r3gq-wxqf-q4gh
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.5.1

## Details
Cross Site Scripting (XSS) vulnerability exists in Gitea before 1.5.1 via the repository settings inside the external wiki/issue tracker URL field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45329
- https://github.com/go-gitea/gitea/pull/4710
- https://blog.gitea.io/2018/09/gitea-1.5.1-is-released
- https://github.com/go-gitea/gitea

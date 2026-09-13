# [H] Gitea Improper Input Validation

## Summary
Severity: High
Advisory: GHSA-q47x-6mqq-4w92
CVE: CVE-2019-11228
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-q47x-6mqq-4w92
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.7.6

## Details
repo/setting.go in Gitea before 1.7.6 and 1.8.x before 1.8-RC3 does not validate the `form.MirrorAddress` before calling `SaveAddress`.

### Specific Go Packages Affected
github.com/go-gitea/gitea/models

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11228
- https://github.com/go-gitea/gitea/pull/6593
- https://github.com/go-gitea/gitea/pull/6595
- https://github.com/go-gitea/gitea/releases/tag/v1.7.6
- https://github.com/go-gitea/gitea/releases/tag/v1.8.0-rc3

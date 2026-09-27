# [H] GitHub Git LFS Arbitrary command execution vulnerability

## Summary
Severity: High
Advisory: GHSA-w4xh-w33p-4v29
CVE: CVE-2017-17831
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w4xh-w33p-4v29
Type: github-advisory

## Affected
- Go: `github.com/git-lfs/git-lfs` — affected >=0 <2.1.1-0.20170519163204-f913f5f9c7c6

## Details
GitHub Git LFS before 2.1.1 allows remote attackers to execute arbitrary commands via an ssh URL with an initial dash character in the hostname, located on a `url =` line in a `.lfsconfig` file within a repository.
### Specific Go Packages Affected
github.com/git-lfs/git-lfs/lfsapi

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17831
- https://github.com/git-lfs/git-lfs/pull/2241
- https://github.com/git-lfs/git-lfs/pull/2242
- https://github.com/git-lfs/git-lfs/commit/f913f5f9c7c6d1301785fdf9884a2942d59cdf19
- https://confluence.atlassian.com/sourcetreekb/sourcetree-security-advisory-2018-01-24-942834324.html
- https://github.com/git-lfs/git-lfs
- https://github.com/git-lfs/git-lfs/releases/tag/v2.1.1
- https://pkg.go.dev/vuln/GO-2021-0073
- https://web.archive.org/web/20200227131639/http://www.securityfocus.com/bid/102926
- http://blog.recurity-labs.com/2017-08-10/scm-vulns
- http://www.securityfocus.com/bid/102926

# [H] github.com/unknwon/cae Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-88jf-7rch-32qc
CVE: CVE-2020-7668
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-88jf-7rch-32qc
Type: github-advisory

## Affected
- Go: `github.com/unknwon/cae` — affected >=0 <1.0.1

## Details
The ExtractTo function doesn't securely escape file paths in zip archives which include leading or non-leading "..". This allows an attacker to add or replace files system-wide.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7668
- https://github.com/unknwon/cae/commit/07971c00a1bfd9dc171c3ad0bfab5b67c2287e11
- https://github.com/unknwon/cae
- https://pkg.go.dev/vuln/GO-2020-0041
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMUNKNWONCAETZ-570384

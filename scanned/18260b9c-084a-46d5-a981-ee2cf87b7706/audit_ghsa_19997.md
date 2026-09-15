# [M] revel is vulnerable to resource exhaustion

## Summary
Severity: Medium
Advisory: GHSA-hggr-p7v6-73p5
CVE: CVE-2020-36568
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-hggr-p7v6-73p5
Type: github-advisory

## Affected
- Go: `github.com/revel/revel` — affected >=0 <1.0.0

## Details
Unsanitized input in the query parser in github.com/revel/revel before v1.0.0 allows remote attackers to cause resource exhaustion via memory allocation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36568
- https://github.com/revel/revel/issues/1424
- https://github.com/revel/revel/pull/1427
- https://github.com/revel/revel/commit/d160ecb72207824005b19778594cbdc272e8a605
- https://github.com/revel/revel
- https://pkg.go.dev/vuln/GO-2020-0003

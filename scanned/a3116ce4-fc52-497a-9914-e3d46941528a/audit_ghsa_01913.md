# [H] Denial of service in GJSON

## Summary
Severity: High
Advisory: GHSA-w942-gw6m-p62c
CVE: CVE-2020-35380
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-w942-gw6m-p62c
Type: github-advisory

## Affected
- Go: `github.com/tidwall/gjson` — affected >=0 <1.6.4

## Details
GJSON before 1.6.4 allows attackers to cause a denial of service via crafted JSON. Due to improper bounds checking, maliciously crafted JSON objects can cause an out-of-bounds panic. If parsing user input, this may be used as a denial of service vector.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35380
- https://github.com/tidwall/gjson/issues/192
- https://github.com/tidwall/gjson/commit/f0ee9ebde4b619767ae4ac03e8e42addb530f6bc
- https://github.com/tidwall/gjson
- https://pkg.go.dev/vuln/GO-2021-0059

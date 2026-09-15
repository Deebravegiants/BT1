# [H] Improper Validation of Array Index in GJSON

## Summary
Severity: High
Advisory: GHSA-p64j-r5f4-pwwx
CVE: CVE-2020-36067
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-p64j-r5f4-pwwx
Type: github-advisory

## Affected
- Go: `github.com/tidwall/gjson` — affected >=0 <1.6.6

## Details
GJSON < 1.6.6 allows attackers to cause a denial of service (panic: runtime error: slice bounds out of range) via a crafted GET call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36067
- https://github.com/tidwall/gjson/issues/196
- https://github.com/tidwall/gjson/commit/bf4efcb3c18d1825b2988603dea5909140a5302b
- https://github.com/tidwall/gjson
- https://pkg.go.dev/vuln/GO-2021-0054

# [H] shiyanhui/dht vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-p6fg-723f-hgpw
CVE: CVE-2020-36562
CWE: CWE-400, CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-p6fg-723f-hgpw
Type: github-advisory

## Affected
- Go: `github.com/shiyanhui/dht` — affected >=0

## Details
Due to unchecked type assertions, maliciously crafted messages can cause panics, which may be used as a denial of service vector.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36562
- https://github.com/shiyanhui/dht/issues/57
- https://github.com/shiyanhui/dht
- https://pkg.go.dev/vuln/GO-2020-0040

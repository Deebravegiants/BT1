# [H] ahh vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-vp56-r7qv-783v
CVE: CVE-2020-36559
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-vp56-r7qv-783v
Type: github-advisory

## Affected
- Go: `github.com/go-aah/aah` — affected >=0 <0.12.4
- Go: `aahframe.work` — affected >=0 <0.12.4

## Details
Due to improper santization of user input, HTTPEngine.Handle allows for directory traversal, allowing an attacker to read files outside of the target directory that the server has permission to read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36559
- https://github.com/go-aah/aah/issues/266
- https://github.com/go-aah/aah/pull/267
- https://github.com/go-aah/aah/commit/881dc9f71d1f7a4e8a9a39df9c5c081d3a2da1ec
- https://github.com/go-aah/aah
- https://pkg.go.dev/vuln/GO-2020-0033

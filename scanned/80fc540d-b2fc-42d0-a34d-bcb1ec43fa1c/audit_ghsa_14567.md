# [H] google.golang.org/protobuf vulnerable to panic leading to denial of service

## Summary
Severity: High
Advisory: GHSA-hw7c-3rfg-p46j
CVE: CVE-2023-24535
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-14
Source: https://github.com/advisories/GHSA-hw7c-3rfg-p46j
Type: github-advisory

## Affected
- Go: `google.golang.org/protobuf` — affected >=1.29.0 <1.29.1

## Details
Parsing invalid messages can panic.

Parsing a text-format message which contains a potential number consisting of a minus sign, one or more characters of whitespace, and no further input will cause a panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24535
- https://github.com/golang/protobuf/issues/1530
- https://github.com/golang/protobuf
- https://go.dev/cl/475995
- https://pkg.go.dev/vuln/GO-2023-1631

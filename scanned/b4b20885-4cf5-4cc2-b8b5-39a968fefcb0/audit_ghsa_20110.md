# [H] Goa vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-fjgq-224f-fq37
CVE: CVE-2019-25073
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-fjgq-224f-fq37
Type: github-advisory

## Affected
- Go: `github.com/goadesign/goa` — affected >=0 <1.4.3
- Go: `goa.design/goa` — affected >=0 <1.4.3
- Go: `goa.design/goa/v3` — affected >=0 <3.0.9

## Details
Improper path santiziation in github.com/goadesign/goa before v3.0.9, v2.0.10, or v1.4.3 allow remote attackers to read files outside of the intended directory

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25073
- https://github.com/goadesign/goa/pull/2388
- https://github.com/goadesign/goa/commit/70b5a199d0f813d74423993832c424e1fc73fb39
- https://github.com/goadesign/goa
- https://pkg.go.dev/vuln/GO-2020-0032

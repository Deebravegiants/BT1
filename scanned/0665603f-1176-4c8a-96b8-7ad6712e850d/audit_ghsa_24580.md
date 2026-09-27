# [H] Out of bounds memory access in github.com/open-policy-agent/opa

## Summary
Severity: High
Advisory: GHSA-x7f3-62pm-9p38
CVE: CVE-2022-28946
CWE: CWE-119
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-20
Source: https://github.com/advisories/GHSA-x7f3-62pm-9p38
Type: github-advisory

## Affected
- Go: `github.com/open-policy-agent/opa` — affected >=0 <0.40.0

## Details
An issue in the component ast/parser.go of Open Policy Agent v0.39.0 causes the application to incorrectly interpret every expression, causing a Denial of Service (DoS) via triggering out-of-range memory access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28946
- https://github.com/open-policy-agent/opa/pull/4548
- https://github.com/open-policy-agent/opa/commit/e9d3828db670cbe11129885f37f08cbf04935264
- https://github.com/open-policy-agent/opa
- https://pkg.go.dev/vuln/GO-2022-0587

# [H] Denial of service in Open Policy Agent 

## Summary
Severity: High
Advisory: GHSA-2m4x-4q9j-w97g
CVE: CVE-2022-33082
CWE: CWE-703
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-2m4x-4q9j-w97g
Type: github-advisory

## Affected
- Go: `github.com/open-policy-agent/opa` — affected >=0 <0.42.0

## Details
An issue in the AST parser (ast/compile.go) of Open Policy Agent v0.10.2 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33082
- https://github.com/open-policy-agent/opa/issues/4761
- https://github.com/open-policy-agent/opa/issues/4762
- https://github.com/open-policy-agent/opa/pull/4701
- https://github.com/open-policy-agent/opa/commit/064f6168a8dfebdeb2ea147f7882bb9f5d2b7f67
- https://github.com/open-policy-agent/opa
- https://github.com/open-policy-agent/opa/blob/598176de326025451025225aca53e85708d5f1db/ast/compile.go#L1224
- https://pkg.go.dev/vuln/GO-2022-0574

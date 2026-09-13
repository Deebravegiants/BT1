# [M] CVE-2026-80051

## Summary
Severity: Medium
Advisory: CVE-2026-80051
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80051
Type: osv

## Details
github.com/graphql-go/graphql (GraphQL for Go) through 0.8.1 does not validate that a scalar variable value matches its declared type. The built-in coerceString and coerceBool functions (scalars.go) accept input whose type does not match the declared String, ID, or Boolean scalar instead of raising the request error that the GraphQL specification mandates. In some cases (but not any typical case of JSON sent to a website), a deeply nested value leads to an unrecoverable "fatal error: stack overflow" condition.

## References
- https://pkg.go.dev
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80051.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80051
- https://github.com/graphql-go/graphql
- https://github.com/graphql-go/graphql/blob/v0.8.1/scalars.go#L307-L315
- https://www.openwall.com/lists/oss-security/2026/08/25/2

# [M] gRPC-Go: xDS RBAC HTTP Filter bypass via mixed-case Header Matching and gRFC A41 validation evasion

## Summary
Severity: Medium
Advisory: GHSA-qc2q-p7wx-3px3
Aliases: CVE-2026-84303
Ecosystem: Go
Published: 2026-09-08
Source: https://osv.dev/vulnerability/GHSA-qc2q-p7wx-3px3
Type: osv

## Affected
- Go: `google.golang.org/grpc` — affected >=0 <1.83.1

## Details
### Summary
A vulnerability in the xDS RBAC HTTP filter implementation in grpc-go allows remote attackers to bypass authorization policies (specifically DENY rules) by using mixed-case or canonical-case header matchers (e.g., X-Role instead of x-role). Additionally, the safety guards introduced by gRFC A41 to block grpc- prefixed headers can be evaded via variations in casing (e.g., Grpc-Status).

### Impact
When an operator defines an RBAC policy referencing headers containing uppercase letters (e.g. X-Role), grpc-go fails to match incoming metadata keys because they are unconditionally lowercased. Because of this case-sensitivity mismatch, a policy designed to block requests containing specific header values fails open: the rule is evaluated as a non-match, and traffic that should have been rejected is served.

Furthermore, gRFC A41 requires rejecting configuration schemas specifying header matchers starting with grpc-. Because this check is executed case-sensitively in grpc-go, attackers can bypass the validation by specifying titles like Grpc-Status.

### Patches
The problem is fixed in `master` and in the 1.83.1 release.

## References
- https://github.com/grpc/grpc-go/security/advisories/GHSA-qc2q-p7wx-3px3
- https://nvd.nist.gov/vuln/detail/CVE-2026-84303
- https://github.com/grpc/grpc-go/pull/9332
- https://github.com/grpc/grpc-go/pull/9335
- https://github.com/grpc/grpc-go/commit/db9482836c298f234c896cf82ab68cafc78237f8
- https://github.com/grpc/grpc-go/commit/ebba6f3f1b206e2b4dc4d1d5a96d18430302c2fe
- https://github.com/grpc/grpc-go
- https://github.com/grpc/grpc-go/releases/tag/v1.83.1

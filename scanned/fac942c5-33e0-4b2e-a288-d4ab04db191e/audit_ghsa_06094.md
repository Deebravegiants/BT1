# [M] Zoo Design Studio: Recursive KCL parsing is vulnerable to denial-of-service

## Summary
Severity: Medium
Advisory: GHSA-jgvr-6x5w-hx5w
CWE: CWE-770
Ecosystem: PyPI, crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-jgvr-6x5w-hx5w
Type: github-advisory

## Affected
- PyPI: `zoo-kcl` — affected >=0 <0.3.129
- crates.io: `kcl-lib` — affected >=0 <0.3.129

## Details
### Impact
Feeding a KCL program that wraps an expression in deep, unnecessary parentheses triggers the parser’s recursive `expression` -> `unnecessarily_bracketed` -> `expression` path. With enough nesting, the call stack grows until it exceeds the process stack limit, causing a stack overflow.

## References
- https://github.com/KittyCAD/modeling-app/security/advisories/GHSA-jgvr-6x5w-hx5w
- https://github.com/KittyCAD/modeling-app

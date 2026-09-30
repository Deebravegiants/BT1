# [M] @asymmetric-effort/nogginlessdom vulnerable to ReDoS via user-controlled regex in HTMLInputElement pattern validation

## Summary
Severity: Medium
Advisory: GHSA-x4hg-hfwf-p9mw
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-x4hg-hfwf-p9mw
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/nogginlessdom` — affected >=0 <0.0.22

## Details
## Summary

The `HTMLInputElement.checkValidity()` method constructed a `RegExp` directly from the user-controlled `pattern` property without any sanitization or timeout protection. This allowed an attacker to inject a regex with catastrophic backtracking, freezing the event loop.

## Fix

Fixed in commit https://github.com/asymmetric-effort/NogginLessDom/commit/25a3cbac665fae5663f8b71c073b80c3152dbe7b on `main`. Added:
- Pattern length limit (1024 characters)
- Nested quantifier detection (`hasNestedQuantifiers`) that rejects patterns like `(a+)+` before constructing the regex
- Patterns exceeding limits are treated as non-matching (safe default)

## References
- https://github.com/asymmetric-effort/NogginLessDom/security/advisories/GHSA-x4hg-hfwf-p9mw
- https://github.com/asymmetric-effort/NogginLessDom/commit/25a3cbac665fae5663f8b71c073b80c3152dbe7b
- https://github.com/asymmetric-effort/NogginLessDom

# [M] joi has an uncaught RangeError on deeply nested input through recursive `link()` schemas

## Summary
Severity: Medium
Advisory: GHSA-q7cg-457f-vx79
CVE: CVE-2026-48038
CWE: CWE-248, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-q7cg-457f-vx79
Type: github-advisory

## Affected
- npm: `joi` — affected >=18.0.0 <18.2.1
- npm: `joi` — affected >=0 <17.13.4

## Details
### Impact
Denial of service via untrapped exception in services validating user-supplied JSON / object input with recursive link schemas. 

The blast radius depends on how the application invokes joi:
- Highest impact: `validate()` called without `try/catch` in a request handler would cause an unhandled exception, potentially crashing the process.
- Lower impact: `validateAsync()` or `validate()` inside a `try/catch`, the validation fails, but the error type is `RangeError` rather than a structured `ValidationError`, complicating error handling.

### Patches
Upgrade to version >= 18.2.1.

### Workarounds
Try/catch the validation to avoid uncaught exceptions.

### References
- Pull request: hapijs/joi#3113

## References
- https://github.com/hapijs/joi/security/advisories/GHSA-q7cg-457f-vx79
- https://github.com/hapijs/joi/pull/3113
- https://github.com/hapijs/joi/commit/2392713d3e9dd91ba752ac0c96e0eaf3d24b9a11
- https://github.com/hapijs/joi

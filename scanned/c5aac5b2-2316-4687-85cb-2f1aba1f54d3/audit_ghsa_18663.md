# [M] Parse Javascript SDK vulnerable to prototype pollution in `Parse.Object` and internal APIs

## Summary
Severity: Medium
Advisory: GHSA-9f2h-7v79-mxw3
CVE: CVE-2025-62374
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-9f2h-7v79-mxw3
Type: github-advisory

## Affected
- npm: `parse` — affected >=0 <7.0.0

## Details
### Summary

Prototype pollution capabilities on various APIs.

### Details

Injection of malicious payload allows attacker to remotely execute arbitrary code. `Parse.Object` and internal APIs are affected, specifically:
- `ParseObject.fromJSON`
- `ParseObject.pin`
- `ParseObject.registerSubclass`
- `ObjectStateMutations` (internal)
- `encode`/`decode` (internal)

### PoC

Demonstrative tests added as part of the fix.

### References

- https://github.com/parse-community/Parse-SDK-JS/security/advisories/GHSA-9f2h-7v79-mxw3
- Patch https://github.com/parse-community/Parse-SDK-JS/releases/tag/7.0.0-alpha.1

## References
- https://github.com/parse-community/Parse-SDK-JS/security/advisories/GHSA-9f2h-7v79-mxw3
- https://nvd.nist.gov/vuln/detail/CVE-2025-62374
- https://github.com/parse-community/Parse-SDK-JS/pull/2749
- https://github.com/parse-community/Parse-SDK-JS/commit/00973987f361368659c0c4dbf669f3897520b132
- https://github.com/parse-community/Parse-SDK-JS
- https://github.com/parse-community/Parse-SDK-JS/releases/tag/7.0.0-alpha.1

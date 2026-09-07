# [M] Parse Server has a protected fields bypass via LiveQuery subscription WHERE clause

## Summary
Severity: Medium
Advisory: GHSA-j7mm-f4rv-6q6q
CVE: CVE-2026-32098
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-j7mm-f4rv-6q6q
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.9
- npm: `parse-server` — affected >=0 <8.6.35

## Details
### Impact

An attacker can exploit LiveQuery subscriptions to infer the values of protected fields without directly receiving them. By subscribing with a WHERE clause that references a protected field (including via dot-notation or `$regex`), the attacker can observe whether LiveQuery events are delivered for matching objects. This creates a boolean oracle that leaks protected field values. The attack affects any class that has both `protectedFields` configured in Class-Level Permissions and LiveQuery enabled.

### Patches

The fix adds validation of the LiveQuery subscription WHERE clause against the class's protected fields, mirroring the existing REST API validation. If a subscription's WHERE clause references a protected field directly, via dot-notation, or inside `$or` / `$and` / `$nor` operators, the subscription is rejected with a permission error. This is applied during subscription creation, so existing event delivery paths are not affected.

### Workarounds

Disable LiveQuery for classes that use `protectedFields` in their Class-Level Permissions, or remove `protectedFields` from classes that require LiveQuery.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-j7mm-f4rv-6q6q
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.9
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.35

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-j7mm-f4rv-6q6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32098
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.35
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.9

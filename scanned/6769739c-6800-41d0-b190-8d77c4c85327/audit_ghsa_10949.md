# [H] Parse Server has a protected fields bypass via dot-notation in query and sort

## Summary
Severity: High
Advisory: GHSA-r2m8-pxm9-9c4g
CVE: CVE-2026-31872
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-r2m8-pxm9-9c4g
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.6.0-alpha.6
- npm: `parse-server` — affected >=0 <8.6.32

## Details
### Impact

The `protectedFields` class-level permission (CLP) can be bypassed using dot-notation in query WHERE clauses and sort parameters. An attacker can use dot-notation to query or sort by sub-fields of a protected field, enabling a binary oracle attack to enumerate protected field values.

This affects both MongoDB and PostgreSQL deployments.

### Patches

The fix ensures that query WHERE clause keys and sort keys are checked against protected fields by extracting the root field from dot-notation paths. For example, a query on `secretObj.apiKey` is now correctly blocked when `secretObj` is a protected field.

### Workarounds

None.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-r2m8-pxm9-9c4g
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.6
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.32

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-r2m8-pxm9-9c4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-31872
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.32
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.6

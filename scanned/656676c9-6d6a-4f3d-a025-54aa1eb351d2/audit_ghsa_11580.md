# [H] Parse Server has a protected fields bypass via logical query operators

## Summary
Severity: High
Advisory: GHSA-72hp-qff8-4pvv
CVE: CVE-2026-30962
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-72hp-qff8-4pvv
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.6
- npm: `parse-server` — affected >=0 <8.6.19

## Details
### Impact

The validation for protected fields only checks top-level query keys. By wrapping a query constraint on a protected field inside a logical operator, the check is bypassed entirely. This allows any authenticated user to query on protected fields to extract field values.

All Parse Server deployments have default protected fields and are vulnerable.

### Patches

The fix adds recursive validation of sub-queries with logical operators, consistent with the existing recursive validation patterns.

### Workarounds

Use a `beforeFind` trigger on affected classes to manually inspect the query for protected field references in logical operator sub-queries and reject the request.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-72hp-qff8-4pvv
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.6
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.19

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-72hp-qff8-4pvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-30962
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.19
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.6

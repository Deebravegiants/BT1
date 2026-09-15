# [C] Parse Server has role escalation and CLP bypass via direct `_Join` table write

## Summary
Severity: Critical
Advisory: GHSA-5f92-jrq3-28rc
CVE: CVE-2026-30966
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-5f92-jrq3-28rc
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.7
- npm: `parse-server` — affected >=0 <8.6.20

## Details
### Impact

Parse Server's internal tables, which store Relation field mappings such as role memberships, can be directly accessed via the REST API or GraphQL API by any client using only the application key. No master key is required.

An attacker can create, read, update, or delete records in any internal relationship table. Exploiting this allows the attacker to inject themselves into any Parse Role, gaining all permissions associated with that role, including full read, write, and delete access to classes protected by role-based Class-Level Permissions (CLP). Similarly, writing to any such table that backs a Relation field used in a `pointerFields` CLP bypasses that access control.

### Patches

The fix blocks direct client access to internal relationship tables in Parse Server's role security enforcement. All create, find, get, update, and delete operations on these tables now require the master key or maintenance key.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-5f92-jrq3-28rc
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.7
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.20

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-5f92-jrq3-28rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30966
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.20
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.7

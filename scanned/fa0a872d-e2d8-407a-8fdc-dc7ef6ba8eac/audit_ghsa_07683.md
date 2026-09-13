# [M] Pimcore vulnerable to SQL injection via unsanitized filter value in Dependency Dao RLIKE clause

## Summary
Severity: Medium
Advisory: GHSA-vxg3-v4p6-f3fp
CVE: CVE-2026-27461
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-vxg3-v4p6-f3fp
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0
- Packagist: `pimcore/pimcore` — affected >=12.0.0 <12.3.3

## Details
The filter query parameter in the dependency listing endpoints is JSON-decoded and the value field is concatenated directly into RLIKE clauses without sanitization or parameterized queries.

Affected code in models/Dependency/Dao.php:
- getFilterRequiresByPath() lines 90, 95, 100
- getFilterRequiredByPath() lines 148, 153, 158

All 6 locations use direct string concatenation like:

    "AND LOWER(CONCAT(o.path, o.key)) RLIKE '".$value."'"

Note that $orderBy and $orderDirection in the same methods (lines 75-81) ARE properly whitelist-validated, but $value has zero sanitization.

Entry points (pimcore/admin-ui-classic-bundle ElementController.php):
- GET /admin/element/get-requires-dependencies (line 654)
- GET /admin/element/get-required-by-dependencies (line 714)

The controller JSON-decodes the filter query param and passes $filter['value'] straight to the Dao without any escaping.

PoC (time-based blind):

    GET /admin/element/get-requires-dependencies?id=1&elementType=document&filter=[{"type":"string","value":"x' OR SLEEP(5)#"}]

If vulnerable, the response is delayed by ~15 seconds (SLEEP runs 3 times, once per UNION arm in the inner subquery).

PoC (error-based extraction):

    GET /admin/element/get-requires-dependencies?id=1&elementType=document&filter=[{"type":"string","value":"x' OR extractvalue(1,concat(0x7e,(SELECT version())))#"}]

Returns the MySQL version string in the error response.

Requires admin authentication. An attacker with admin panel access can extract the full database including password hashes of other admin users.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-vxg3-v4p6-f3fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27461
- https://github.com/pimcore/pimcore/pull/18991
- https://github.com/pimcore/pimcore/commit/1c3925fbec4895abeb21e5c244a83679c4e4a6f4
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.3

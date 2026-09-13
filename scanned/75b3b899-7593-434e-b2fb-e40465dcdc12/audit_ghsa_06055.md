# [C] CodeIgniter: SQL injection in Query Builder deleteBatch() when used with where() conditions

## Summary
Severity: Critical
Advisory: GHSA-c9w5-rwh3-7pm9
CVE: CVE-2026-63221
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-c9w5-rwh3-7pm9
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=4.3.0 <4.7.4

## Details
### Impact
A SQL injection vulnerability exists in the Query Builder's `deleteBatch()` method. When `deleteBatch()` is used together with `where()` conditions, the bound values from the `WHERE` clause are substituted directly into the generated SQL **with their escape flag ignored**, so they are never escaped or quoted. If an application passes user-controlled input to `where()` before calling `deleteBatch()`, that input is interpreted as SQL rather than as a value, allowing SQL injection.

This affects only the `deleteBatch()` code path. Regular `delete()` operations escape `where()` binds correctly.

### Patches
Upgrade to v4.7.4 or later.

### Workarounds
If you cannot upgrade immediately:

- Strictly validate and cast values (e.g. numeric IDs) before using them in conditions - though this does not fully protect string conditions.
- Do not pass user-controlled input to `where()` when using `deleteBatch()`.
- For user-controlled conditions, use a normal `delete()` with Query Builder binds instead of `deleteBatch(`).
- Where possible, express required matching values through the batch data and `onConstraint()` rather than as separate user-controlled `where()` clauses.

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-c9w5-rwh3-7pm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-63221
- https://github.com/codeigniter4/CodeIgniter4/commit/f5e463b9a3e986389ce285963e51a7f1fab6559f
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/releases/tag/v4.7.4

# [M] October CMS has Safe Mode Bypass via Twig Database Write Operations

## Summary
Severity: Medium
Advisory: GHSA-h6jm-f4hh-fw27
CVE: CVE-2026-26274
CWE: CWE-184, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-h6jm-f4hh-fw27
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <3.7.14
- Packagist: `october/october` — affected >=4.0.0 <4.1.10

## Details
A vulnerability was identified in the Twig sandbox security policy that allowed database write operations when `cms.safe_mode` is enabled. Backend users with Developer permissions could use Twig template markup to execute insert, update, and delete operations on any database table through the query builder, which is included in the sandbox allow-list.

### Impact
- Arbitrary database writes including modification or deletion of any table
- Requires authenticated backend access with Developer permissions
- Only relevant when `cms.safe_mode` is enabled (otherwise direct PHP injection is already possible)

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. Write operations such as `insert`, `update`, `delete`, and `truncate` are now blocked on query builder and model objects within the Twig sandbox. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Restrict Developer tool access to fully trusted administrators only

### Reporter
- Reported by [Chris Alupului](https://github.com/neosprings)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-h6jm-f4hh-fw27
- https://nvd.nist.gov/vuln/detail/CVE-2026-26274
- https://github.com/octobercms/october

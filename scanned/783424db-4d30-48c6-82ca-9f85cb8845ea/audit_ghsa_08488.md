# [M] SQLAdmin: Authorization Bypass on `ajax_lookup`

## Summary
Severity: Medium
Advisory: GHSA-54mc-gghv-4cfj
CVE: CVE-2026-46645
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-54mc-gghv-4cfj
Type: github-advisory

## Affected
- PyPI: `sqladmin` — affected >=0 <0.25.1

## Details
### Impact

The `ajax_lookup` endpoint in `application.py` bypasses the `is_accessible()` access control check that all other endpoints enforce.

If a developer restricts model access by overriding `is_accessible()`, an authenticated user can still query that model's data through the `ajax_lookup` endpoint — silently bypassing the restriction.

**Affected endpoint:**

`GET /{identity}/ajax/lookup?name=<field>&term=<query>`

**All other endpoints enforce both checks:**

| Endpoint | `@login_required` | `is_accessible()` |
|---|---|---|
| `list` | ✓ | ✓ |
| `create` | ✓ | ✓ |
| `edit` | ✓ | ✓ |
| `delete` | ✓ | ✓ |
| `details` | ✓ | ✓ |
| `export` | ✓ | ✓ |
| `ajax_lookup` (before fix) | ✗ | ✗ |
| `ajax_lookup` (after fix) | ✓ | ✓ |

Note: before this fix, `ajax_lookup` also lacked the `@login_required` decorator — unauthenticated users could query it directly. That was addressed in #1035. This report covers the remaining gap: authenticated but unauthorized users.

### Patches

Two changes were made to `ajax_lookup`:

1. Replaced the hand-rolled authentication check added in #1035 with the standard `@login_required` decorator used by all other endpoints.
2. Added the missing `is_accessible(request)` check, raising `HTTP 403` when it returns `False`.

### Workarounds

None. Developers relying on `is_accessible()` to restrict model visibility are exposed regardless of what other access controls are in place.

## References
- https://github.com/smithyhq/sqladmin/security/advisories/GHSA-54mc-gghv-4cfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-46645
- https://github.com/smithyhq/sqladmin/pull/1035
- https://github.com/smithyhq/sqladmin/commit/b0d3a19fb9b074a9ed243de46930108375dfbb98
- https://github.com/smithyhq/sqladmin
- https://github.com/smithyhq/sqladmin/releases/tag/0.25.1

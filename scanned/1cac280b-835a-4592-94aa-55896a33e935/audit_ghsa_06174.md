# [M] Starlette-Admin's unvalidated `order_by` parameter allows ordering by hidden columns (info-exposure oracle) and HTTP 500 DoS

## Summary
Severity: Medium
Advisory: GHSA-6753-gr46-6wpr
CVE: CVE-2026-54553
CWE: CWE-200, CWE-248, CWE-602, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-6753-gr46-6wpr
Type: github-advisory

## Affected
- PyPI: `starlette-admin` — affected >=0 <0.16.1

## Details
## Summary

Affected versions of Starlette-Admin prior to 0.16.1 do not properly validate user-supplied sort and search parameters against the configured field allowlists. While the administrative UI restricts available fields based on field configuration, the backend accepts arbitrary field names supplied through API requests.

An authenticated user can submit crafted requests to sort or filter records using fields that are not intended to be searchable or sortable. Additionally, supplying invalid field names or special Python attribute names can trigger unhandled exceptions that result in HTTP 500 responses.

## Impact

An authenticated user with access to affected list endpoints may:

* Bypass intended UI restrictions and perform sorting or filtering on fields that are not configured as searchable or sortable.
* Cause affected API requests to fail with HTTP 500 responses by supplying invalid field names or special Python attribute names such as `metadata` or `__class__`.

This vulnerability may result in unauthorized use of query functionality and limited denial-of-service conditions affecting the targeted endpoint.

## Affected Versions

All versions before 0.16.1.

## Patched Versions

* 0.16.1

## Workarounds

There are no known workarounds. Users should upgrade to version 0.16.1 or later.

## References
- https://github.com/jowilf/starlette-admin/security/advisories/GHSA-6753-gr46-6wpr
- https://github.com/jowilf/starlette-admin/pull/776
- https://github.com/jowilf/starlette-admin/commit/af05b45cd90944b726949fd650ab9d19f1abafc3
- https://github.com/jowilf/starlette-admin/commit/d2a25ebbaf213d4c2cfc87187e34309ca6e30a51
- https://github.com/jowilf/starlette-admin
- https://github.com/jowilf/starlette-admin/releases/tag/0.16.1

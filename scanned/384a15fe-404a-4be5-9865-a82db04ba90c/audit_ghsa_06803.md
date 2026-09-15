# [M] Kimai: ExportTemplate CRUD Missing Authorization Check Allows Unauthorized TEAMLEAD Access

## Summary
Severity: Medium
Advisory: GHSA-rw46-qg69-vg6h
CVE: CVE-2026-52828
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-rw46-qg69-vg6h
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.58.0

## Details
### Summary

The `ExportController` web routes for creating and editing export templates are gated only by the class-level `create_export` permission, which is granted to `ROLE_TEAMLEAD` by default. The corresponding API routes and UI button visibility correctly require the stricter `create_export_template` permission, which is granted only to `ROLE_ADMIN` and `ROLE_SUPER_ADMIN`. A TEAMLEAD user can directly access the template create/edit routes to create or modify global export templates that are visible to all users including administrators.

### Details

The `ExportController` applies the class-level annotation `#[IsGranted('create_export')]`.

The `createExportTemplate` (line 210) and `editExportTemplate` (line 220) methods have no method-level `#[IsGranted('create_export_template')]` annotation. The permission hierarchy in `config/packages/kimai.yaml:103,115,122-123` grants `create_export` to `ROLE_TEAMLEAD` via the `EXPORT` permission set, but `create_export_template` only to `ROLE_ADMIN` and `ROLE_SUPER_ADMIN`.

The API controller correctly requires `create_export_template`. The UI template (`templates/export/index.html.twig:124`) correctly hides the create button behind `create_export_template`. Only the web controller routes are missing the check.

`ExportTemplate` entities are global — they have no per-user or per-team scoping (`src/Entity/ExportTemplate.php:19-56`). Any template created or modified by a TEAMLEAD which is marked as "Available for all users" is visible to and usable by every user in the instance.

*A PoC was provided, but removed for security reasons.*

### Impact

Any user with `ROLE_TEAMLEAD` can create and modify global export templates intended to be managed only by administrators. The templates control the structure and content of exported data (columns, renderer, format). While the impact is limited to data integrity manipulation of a non-security-critical resource (no RCE, no credential exposure), it violates the intended permission boundary and allows a lower-privileged user to influence the data output format used by all users including administrators.

# Solution

The permission check `#[IsGranted('create_export_template')]` was added to the `ExportController` covering the methods `createExportTemplate()` and `editExportTemplate`.

See [https://www.kimai.org/en/security/ghsa-rw46-qg69-vg6h](https://www.kimai.org/en/security/ghsa-rw46-qg69-vg6h) for more details.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-rw46-qg69-vg6h
- https://github.com/kimai/kimai

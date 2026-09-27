# [M] Laravel Backpack CRUD: HasUploadFields keeps the attacker-supplied file extension — public-disk uploads of `shell.php` reach the webserver

## Summary
Severity: Medium
Advisory: GHSA-8q2w-pv9p-mjvc
CVE: CVE-2026-54177
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8q2w-pv9p-mjvc
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.14
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.38

## Details
## Summary

`HasUploadFields` (used via `CrudTrait` on Backpack-managed models) and the `withFiles()` uploader preserve the client-supplied file extension without validation. On installations using a `public` disk with `php artisan storage:link`, this allows an authenticated administrator to upload a file with a server-executable extension that the web server will pass to the PHP interpreter - if no MIME or other type of upload validation is present.

## Details

The `uploadFileToDisk` and `uploadMultipleFilesToDisk` methods hash the filename stem but write the client-supplied extension to disk verbatim — no allowlist, blocklist, or MIME check is applied inside the trait itself.

The newer `withFiles()` path (via `FileNameGenerator`) resolves the extension from the file's MIME type rather than the client filename, but also does not block server-executable types.

Applications that follow the Backpack quickstart without adding explicit `mimes:` or `mimetypes:` validation rules in their form requests are affected.

## Impact

An authenticated administrator with access to an upload-enabled CRUD panel, on a site using the `public` disk with web-accessible storage and no MIME type validation, can upload a server-executable file and achieve remote code execution.

**Conditions required for exploitation:**

- Authenticated admin access to a Backpack CRUD panel
- An upload field with no `mimes:` / `mimetypes:` validation rule
- The `public` disk in use (standard pattern for web-visible uploads)
- `php artisan storage:link` in place
- A web server + PHP-FPM stack (default on most hosts)

## Fix

A denylist for server-executable extensions has been added to both `HasUploadFields` and `FileNameGenerator`. Image-typed fields now additionally enforce an allowlist. This is defence-in-depth — it does not replace application-level validation.

## Recommended developer action

Review all upload fields and add explicit `mimes:` or `mimetypes:` validation in your form requests or field definitions. Refer to the [Backpack field documentation](https://backpackforlaravel.com/docs) for examples.

---

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304)) via sechub.dev.

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-8q2w-pv9p-mjvc
- https://github.com/Laravel-Backpack/CRUD/pull/5993
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.14
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.38

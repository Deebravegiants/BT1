# [H] NukeViet: Path Traversal to Arbitrary File Deletion in Edit Comment Function

## Summary
Severity: High
Advisory: GHSA-c9xg-64p9-f2jj
CVE: CVE-2026-54065
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-c9xg-64p9-f2jj
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.6.00

## Details
## Summary

Path Traversal to Arbitrary File Deletion in the Edit Comment admin function. An authenticated administrator can delete arbitrary files within the application root (e.g., `config.php`) by injecting a crafted `attach` parameter, rendering the application inoperable.

## Affected Component

`modules/comment/admin/edit.php`

## Root Cause

In the vulnerable version, the `attach` parameter received via HTTP POST was not validated before being processed:

```php
// Vulnerable code (before fix)
$attach = $nv_Request->get_string('attach', 'post', '', true);
if (!empty($attach)) {
    $attach = substr($attach, strlen(NV_BASE_SITEURL . NV_UPLOADS_DIR . '/' . $module_upload . '/'));
}
```

`substr()` strips the first N characters (equal to the length of the upload URL prefix, e.g. 26 chars for `/nukeviet/uploads/comment/`). By padding the payload with exactly 26 arbitrary characters followed by a path traversal sequence, an attacker can store `../../<target>` directly into the database.

When the comment is subsequently deleted, `del.php` reads `attach` from the database and calls:

```php
nv_deletefile(NV_UPLOADS_REAL_DIR . '/' . $module_upload . '/' . $row['attach']);
```

`nv_deletefile()` resolves the path via `realpath()` and only verifies the result is within `NV_ROOTDIR` — it does **not** restrict deletion to the uploads directory — allowing deletion of any file in the installation root.

## Steps to Reproduce

1. Log in as an administrator and navigate to **Admin → Comment Management**.
2. Select any comment and open the Edit form.
3. Intercept the POST request and set the `attach` parameter to:

```
aaaaaaaaaaaaaaaaaaaaaaaaaa../../config.php
```

*(26 padding characters + traversal path)*

4. Submit the request. The value `../../config.php` is now stored in the database.
5. Delete the comment. `config.php` is deleted from the application root.
6. The application immediately redirects to the install wizard, confirming the file has been removed.

## Impact

- Any file readable by the web server process within `NV_ROOTDIR` can be permanently deleted.
- Deleting `config.php` causes a full application outage and exposes the install wizard.

## Severity

**CVSS v3.1 Base Score: 8.7 (High)**

```
CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H
```

| Metric | Value |
|--------|-------|
| Attack Vector | Network |
| Attack Complexity | Low |
| Privileges Required | High (Admin required) |
| User Interaction | None |
| Scope | Changed |
| Confidentiality | None |
| Integrity | High |
| Availability | High |

## Fix

Added `nv_is_file()` validation before processing the `attach` value. This function uses `realpath()` and a regex check to ensure the file resolves to a path within the intended upload directory, rejecting any traversal attempts.

```php
// Fixed code
$attach = $nv_Request->get_string('attach', 'post', '');
if (!empty($attach) and nv_is_file($attach, NV_UPLOADS_DIR . '/' . $module_upload)) {
    $attach = substr($attach, strlen(NV_BASE_SITEURL . NV_UPLOADS_DIR . '/' . $module_upload . '/'));
} else {
    $attach = '';
}
```

## References
- https://github.com/nukeviet/nukeviet/security/advisories/GHSA-c9xg-64p9-f2jj
- https://github.com/nukeviet/nukeviet

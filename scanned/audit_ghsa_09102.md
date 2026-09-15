# [M] CI4MS Vulnerable to Arbitrary Database Table Drop via Theme deleteProcess

## Summary
Severity: Medium
Advisory: GHSA-vgrf-pr28-vf98
CVE: CVE-2026-41890
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-vgrf-pr28-vf98
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0.31.1.0 <0.31.8.0

## Details
### Summary
The `deleteProcess()` action accepts a POST parameter `tables[]` containing arbitrary table names. These are passed directly to `$forge->dropTable()` without validating that the tables belong to the theme being deleted.

The `deleteConfirm` view correctly populates `tables[]` from the theme's own migration files, but the server-side `deleteProcess` does not verify the received values against those files. An authenticated admin can craft a POST request with arbitrary table names and drop any table in the database.

This is a real bug even within the admin trust model: the action should be scoped to the theme's own tables. The permission grants  delete this theme's data", not "drop any table".

### Details

### Location
`modules/Theme/Controllers/Theme.php` :: `deleteProcess()` ~line 147

### Vulnerable Code
```php
public function deleteProcess(string $slug)
{
    $themeName = $slug;
    $activeTheme = setting('App.siteTheme');
    if ($activeTheme === $themeName) {
        return redirect()->route('templateSettings')...;
    }

    $tablesToDrop = $this->request->getPost('tables');  // ← user-supplied, unvalidated
    if (!empty($tablesToDrop) && is_array($tablesToDrop)) {
        $forge = \Config\Database::forge();
        $db    = \Config\Database::connect();
        foreach ($tablesToDrop as $table) {
            if ($db->tableExists($table)) {
                $forge->dropTable($table, true);  // ← no whitelist check
            }
        }
    }
```

### PoC
1. Authenticate to the backend (any user with theme.delete permission)
2. POST to `/backend/themes/delete-process/<any_non_active_theme_slug>`
3. Include `tables[]=<any_table>` in POST body
4. The named tables are dropped without validation

### Impact
- Dropped `ci4ms_blog` (confirmed in test)
- Dropped `ci4ms_users` + `ci4ms_auth_identities` simultaneously — disables all authentication (confirmed)
- Any table in the database can be targeted

### Additional note
Quick note on the design intent for deleteProcess — I noticed delete_confirm.php scopes the checkboxes to the theme's own migration files, and the CHANGELOG confirms the selective deletion was intentional (admins can choose which tables to keep). The server-side deleteProcess already has all the information it needs to validate the input — deleteConfirm derives the valid table set from the migration files, deleteProcess just needs to do the same before acting on the POST. Happy to clarify if useful.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-vgrf-pr28-vf98
- https://nvd.nist.gov/vuln/detail/CVE-2026-41890
- https://github.com/ci4-cms-erp/ci4ms/commit/2f38284281ce6b435ea42003951f14109ac2cea7
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.8.0

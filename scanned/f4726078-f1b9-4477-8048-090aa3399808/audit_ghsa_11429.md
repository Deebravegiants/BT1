# [H] Admidio has a Second-Order SQL Injection via List Configuration (lsc_special_field, lsc_sort, lsc_filter)

## Summary
Severity: High
Advisory: GHSA-3x67-4c2c-w45m
CVE: CVE-2026-32813
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-3x67-4c2c-w45m
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.7

## Details
## Summary

The MyList configuration feature in Admidio allows authenticated users to define custom list column layouts. User-supplied column names, sort directions, and filter conditions are stored in the `adm_list_columns` table via prepared statements (safe storage), but are later read back and interpolated directly into dynamically constructed SQL queries without sanitization or parameterization. This is a classic second-order SQL injection: safe write, unsafe read.

An attacker can inject arbitrary SQL through these stored values to read, modify, or delete any data in the database, potentially achieving full database compromise.

## Details

### Step 1: Storing the Payload (Safe Write)

In `modules/groups-roles/mylist_function.php` (lines 89-115), user-supplied POST array values for column names, sort directions, and filter conditions are accepted. The only validation on column values is a prefix check (must start with `usr_` or `mem_`). Sort and condition values have no validation at all. These values are stored in the database via `ListConfiguration::addColumn()` which calls `Entity::save()` using prepared statements -- so the INSERT/UPDATE is safe.

Key source file references:
- `D:\bugcrowd\admidio\repo\modules\groups-roles\mylist_function.php` lines 89-115
- `D:\bugcrowd\admidio\repo\src\Roles\Entity\ListConfiguration.php` lines 106-116

### Step 2: Triggering the Payload (Unsafe Read)

When the list is viewed (via `lists_show.php`), `ListConfiguration::getSql()` reads the stored values and interpolates them directly into SQL in four locations:

**Injection Point 1 -- lsc_special_field in SELECT clause:**
File `D:\bugcrowd\admidio\repo\src\Roles\Entity\ListConfiguration.php` lines 739-770.
The `lsc_special_field` value is read from the database and used as a column name in the SELECT clause. Only three values (`mem_duration`, `mem_begin`, `mem_end`) get special handling; all others fall through to the `default` case where the raw value is used directly as both `$dbColumnName` and `$sqlColumnName`, then interpolated into the SQL as `$dbColumnName AS $sqlColumnName`.

**Injection Point 2 -- lsc_sort in ORDER BY clause:**
File `D:\bugcrowd\admidio\repo\src\Roles\Entity\ListConfiguration.php` lines 790-792.
The `lsc_sort` value is appended directly after the column name in the ORDER BY clause.

**Injection Point 3 -- lsc_special_field in search conditions:**
File `D:\bugcrowd\admidio\repo\src\Roles\Entity\ListConfiguration.php` lines 611-621.
The `lsc_special_field` value is interpolated into COALESCE() expressions used in search WHERE conditions.

**Injection Point 4 -- lsc_filter via ConditionParser:**
File `D:\bugcrowd\admidio\repo\src\Roles\ValueObject\ConditionParser.php` line 347.
The ConditionParser appends raw characters from the stored filter value to the SQL string. A single quote can break out of the SQL string context.

### Root Cause

The `addColumn()` method and `mylist_function.php` accept arbitrary strings for column names, sort directions, and filter conditions. The only gate for column names is a prefix check (`usr_` or `mem_`), which is trivially satisfied by an attacker (e.g., `usr_id) UNION SELECT ...`). No allowlist of valid column names exists. No server-side validation of sort values exists (should only allow ASC/DESC/empty). The frontend `<select>` element only offers ASC/DESC, but this is trivially bypassed by POSTing arbitrary values.

## PoC

**Prerequisites:** Logged-in user with list edit permission (default: all logged-in users).

**Step 1: Save a list config with SQL injection in lsc_special_field**

```
curl -X POST "https://TARGET/adm_program/modules/groups-roles/mylist_function.php?mode=save_temporary" \
  -H "Cookie: ADMIDIO_SESSION_ID=<session>" \
  -d "adm_csrf_token=<csrf_token>" \
  -d "column[]=usr_login_name" \
  -d "column[]=usr_id FROM adm_users)--" \
  -d "sort[]=" \
  -d "sort[]=" \
  -d "condition[]=" \
  -d "condition[]=" \
  -d "sel_roles[]=<valid_role_uuid>"
```

The second column value `usr_id FROM adm_users)--` starts with `usr_` so it passes the prefix check. When read back in `getSql()`, it is interpolated directly as a column expression in the SQL SELECT clause.

**Step 2: Sort-based injection (simpler, no prefix check needed)**

```
curl -X POST "https://TARGET/adm_program/modules/groups-roles/mylist_function.php?mode=save_temporary" \
  -H "Cookie: ADMIDIO_SESSION_ID=<session>" \
  -d "adm_csrf_token=<csrf_token>" \
  -d "column[]=usr_login_name" \
  -d "sort[]=ASC,(SELECT+CASE+WHEN+(1=1)+THEN+1+ELSE+1/0+END)" \
  -d "condition[]=" \
  -d "sel_roles[]=<valid_role_uuid>"
```

This injects into the ORDER BY clause. The sort value has zero server-side validation.

**Step 3:** The `save_temporary` mode automatically redirects to `lists_show.php` which calls `ListConfiguration::getSql()`, executing the injected SQL.

## Impact

- **Data Exfiltration:** An attacker can extract any data from the database including password hashes, email addresses, personal data of all members, and application configuration.
- **Data Modification:** With stacked queries (supported by MySQL with PDO), the attacker can modify or delete data.
- **Privilege Escalation:** Password hashes can be extracted and cracked, or admin accounts can be directly modified.
- **Full Database Compromise:** The entire database is accessible through this vulnerability.

The attack requires authentication and CSRF token, but:
1. Any logged-in user has this permission by default (when `groups_roles_edit_lists = 1`).
2. The CSRF token is available in the same session.
3. The injected payload persists in the database and triggers every time anyone views the list.

## Recommended Fix

### Fix 1: Allowlist for lsc_special_field

Add a strict allowlist of valid special field names before calling `addColumn()` in `mylist_function.php`. The list should match exactly the field names supported in `getSql()` and the JavaScript on `mylist.php`.

### Fix 2: Validate lsc_sort values

In `ListConfiguration::addColumn()`, validate that the sort parameter is one of ASC, DESC, or empty string before storing it.

### Fix 3: Defense-in-depth validation in ListConfiguration::getSql()

Also validate the `lsc_special_field` value against an allowlist in `getSql()` before interpolating it into the SQL string. This protects against payloads already stored in the database.

### Fix 4: Escape filter values in ConditionParser

Use parameterized queries or at minimum escape single quotes in `ConditionParser::makeSqlStatement()`.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-3x67-4c2c-w45m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32813
- https://github.com/Admidio/admidio/commit/3473bf5a7aa1bfc5043e73979719396276f4189f
- https://github.com/Admidio/admidio

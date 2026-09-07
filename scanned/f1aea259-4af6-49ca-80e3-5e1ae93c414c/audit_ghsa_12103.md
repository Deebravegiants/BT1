# [H] AVideo has SQL Injection in category.php fixCleanTitle() via Unparameterized clean_title and id Variables

## Summary
Severity: High
Advisory: GHSA-584p-rpvq-35vf
CVE: CVE-2026-33770
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-584p-rpvq-35vf
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

The `fixCleanTitle()` static method in `objects/category.php` constructs a SQL SELECT query by directly interpolating both `$clean_title` and `$id` into the query string without using prepared statements or parameterized queries. An attacker who can trigger category creation or renaming with a crafted title value can inject arbitrary SQL.

### Details

**File:** `objects/category.php`

**Vulnerable code:**
```php
public static function fixCleanTitle($clean_title, $count, $id, $original_title = "")
{
    global $global;

    $sql = "SELECT * FROM categories WHERE clean_name = '{$clean_title}' ";
    if (!empty($id)) {
        $sql .= " AND id != {$id} ";
    }
    $sql .= " LIMIT 1";
    $res = sqlDAL::readSql($sql, "", [], true);
    // ...
}
```

Both `$clean_title` (a user-supplied category name after slug conversion) and `$id` (the category ID being edited) are embedded directly into the SQL string. The `$clean_title` value derives from user input through the category save workflow — it is the "clean" URL-slug version of whatever category name the user submits. No escaping or parameterization is applied before the value is placed inside single quotes in the query.

### PoC

An authenticated admin creates or renames a category with the title:
```
test' UNION SELECT username,password,3,4,5,6,7,8,9,10 FROM users-- -
```

After slug conversion (which typically only strips spaces and special characters, leaving SQL metacharacters that survive inside single quotes), the backend executes:
```sql
SELECT * FROM categories WHERE clean_name = 'test' UNION SELECT username,password,3,4,5,6,7,8,9,10 FROM users-- -'  LIMIT 1
```

This returns rows from the `users` table, enabling full credential exfiltration. The `$id` concatenation point is also injectable via a crafted numeric+SQL-suffix value if integer validation is absent.

### Impact

- **Type:** SQL Injection (CWE-89)
- **Severity:** High
- **Authentication required:** Admin-level (category management), though the same pattern may be reachable via lower-privilege paths depending on plugin configuration
- **Impact:** Full database read; credentials, private video metadata, user PII accessible via UNION injection
- **Fix:** Replace direct interpolation with parameterized queries — use `?` placeholders and pass `$clean_title` and `(int)$id` as bound parameters

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-584p-rpvq-35vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33770
- https://github.com/WWBN/AVideo/commit/994cc2b3d802b819e07e6088338e8bf4e484aae4
- https://github.com/WWBN/AVideo

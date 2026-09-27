# [M] Arcane Backend: OS Command Injection in Volume Browser ListDirectory via path query parameter

## Summary
Severity: Medium
Advisory: GHSA-9mvm-4gwg-v8mp
CVE: CVE-2026-45626
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-9mvm-4gwg-v8mp
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0

## Details
## Summary

`GET /environments/{id}/volumes/{volumeName}/browse` accepts a `path` query parameter that is passed to a shell command (`sh -c "find … | while …"`) inside an Arcane helper container. The path sanitiser blocks `../` traversal but does not strip Bourne-shell metacharacters such as `$()` or backticks, and `strconv.Quote` only escapes Go string metacharacters, not shell substitution sequences. Any authenticated user with access to a browseable volume can execute arbitrary commands inside the helper container; command output is reflected back in the 500 error body.

## Details

The execution flow is:

1. `BrowseDirectoryInput.Path` (query: `path`) — `backend/internal/huma/handlers/volumes.go:148`
2. `VolumeHandler.BrowseDirectory` calls `volumeService.ListDirectory(ctx, volumeName, input.Path)` — `backend/internal/huma/handlers/volumes.go:858-865`. Note the route registration at line 412–419 only declares `BearerAuth`/`ApiKeyAuth`; there is no `checkAdmin(ctx)` call (compare with `customize.go`, `system.go`, `swarm.go`, etc., which do enforce admin).
3. `VolumeService.ListDirectory` runs the user-supplied path through `sanitizeBrowsePathInternal`, then joins it under `/volume`, quotes it with `strconv.Quote`, and embeds it into a `sh -c` command:

```go
// backend/internal/services/volume_service.go:286-300
sanitizedPath, err := s.sanitizeBrowsePathInternal(dirPath)
...
targetPath := path.Join("/volume", sanitizedPath)
quotedPath := strconv.Quote(targetPath)
cmd := []string{"sh", "-c", fmt.Sprintf(
    "find %s -mindepth 1 -maxdepth 1 | while IFS= read -r f; do out=$(stat -c \"%%s %%Y %%f %%A\" -- \"$f\" 2>/dev/null) || continue; printf \"%%s\\0%%s\\0\" \"$f\" \"$out\"; done",
    quotedPath)}
stdout, _, err := s.execInContainerInternal(ctx, containerID, cmd)
```

The sanitiser is insufficient (`backend/internal/services/volume_service.go:1448-1467`):

```go
func (s *VolumeService) sanitizeBrowsePathInternal(input string) (string, error) {
    trimmed := strings.TrimSpace(input)
    if trimmed == "" || trimmed == "/" { return "/", nil }
    cleaned := path.Clean(trimmed)
    if !path.IsAbs(cleaned) { cleaned = "/" + cleaned }
    if strings.Contains(cleaned, "/../") || strings.HasSuffix(cleaned, "/..") || cleaned == "/.." {
        return "", fmt.Errorf("invalid path: path traversal not allowed")
    }
    if !strings.HasPrefix(cleaned, "/") { return "", fmt.Errorf("invalid path: must be absolute") }
    return cleaned, nil
}
```

Only `../` patterns are filtered. `$(...)`, backticks, `;`, `&`, `|`, `>`, etc. all pass through unchanged. `strconv.Quote` then wraps the path in Go-style double quotes, which `sh -c` interprets as a regular double-quoted string — and bash performs `$(...)` command substitution inside double quotes.

For the input `/$( id)`:
- `sanitizeBrowsePathInternal` returns `/$( id)` (no `../` present).
- `path.Join("/volume", "/$( id)")` → `/volume/$( id)`.
- `strconv.Quote(...)` → `"/volume/$( id)"`.
- The shell runs `find "/volume/$( id)" …`, which expands to `find "/volume/uid=0(root) gid=0(root) groups=0(root)" …`. `find` fails because that path does not exist; the stderr containing the substituted command output is propagated by `execInContainerInternal` (volume_service.go:910-918) into a `command exited with code N: …` error, then re-wrapped by `ListDirectory` and returned to the client as a 500 response body.

Errors from the handler at `volumes.go:863-864` are returned via `huma.Error500InternalServerError(err.Error())`, so the substituted output is reflected in plaintext.

**Blast radius / mitigations actually present:**
- The helper container is created by `createTempContainerInternal` with `NetworkDisabled: true`, no privileged mode, no Docker socket mount, only the target Docker volume bind-mounted (`:ro` for browse). It is auto-removed.
- Therefore the injection executes inside an isolated, network-disabled container that already has read access to the same files the browse API exposes.
- However: the injection grants arbitrary command execution within that container (well beyond the find/stat/readlink/head primitives the API exposes), enables data exfiltration via error-message side channel, and lets an attacker probe the helper image / volume in ways the legitimate API forbids (e.g. read symlink targets the API explicitly censors at `volume_service.go:336-356`, read past size limits, etc.).
- A non-admin authenticated Arcane user is sufficient (no role check on the volumes browser routes), which makes this a privilege/capability extension for users who otherwise cannot run arbitrary `docker exec`.

**Secondary issue (same sanitiser):** `DeleteFile` (`volume_service.go:924-963`) defends against deleting volume root with `if sanitizedPath == "/"`. Input `path=.` yields `path.Clean(".") == "."` → prefixed to `/.`, which fails the `== "/"` check, then `path.Join("/volume", "/.") == "/volume"`, so the executed command is `rm -rf /volume`, recursively deleting all volume contents. This is a separate logic flaw worth fixing alongside the sanitiser hardening but is reported here only for completeness.

## Impact

- Authenticated user (any role, including non-admin) can execute arbitrary shell commands inside the per-volume helper container.
- Output of those commands is reflected in HTTP 500 error bodies — usable as an exfiltration channel.
- Attacker gains capabilities the legitimate API withholds: bypass the symlink-target censoring at `volume_service.go:336-356`, bypass per-file byte limits, enumerate the helper image, mount-time inspection, etc.
- No host compromise: the container has `NetworkDisabled: true`, no privileged flag, no Docker socket; the volume is bind-mounted read-only for browse. Confidentiality/integrity/availability impact is therefore limited (CVSS C:L / I:L / A:L) but real.
- The same insufficient sanitiser additionally permits a destructive `rm -rf /volume` by sending `path=.` to `DELETE /environments/{id}/volumes/{volumeName}/browse`, which any authenticated user can also reach.

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-9mvm-4gwg-v8mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45626
- https://github.com/getarcaneapp/arcane

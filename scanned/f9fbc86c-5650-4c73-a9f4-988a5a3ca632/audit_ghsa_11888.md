# [H] FileBrowser has Path Traversal in Public Share Links that Exposes Files Outside Shared Directory

## Summary
Severity: High
Advisory: GHSA-mr74-928f-rw69
CVE: CVE-2026-28492
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-mr74-928f-rw69
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.61.0

## Details
### Summary
When a user creates a public share link for a **directory**, the `withHashFile` middleware in `http/public.go` (line 59) uses `filepath.Dir(link.Path)` to compute the `BasePathFs` root. This sets the filesystem root to the **parent directory** instead of the shared directory itself, allowing anyone with the share link to browse and download files from all sibling directories.

### Details
In `http/public.go` lines 52-64, the `withHashFile` function handles public share link requests:

```go
basePath := link.Path    // e.g. "/documents/shared"
filePath := ""

if file.IsDir {
    basePath = filepath.Dir(basePath)  // BUG: becomes "/documents" (parent!)
    filePath = ifPath
}

d.user.Fs = afero.NewBasePathFs(d.user.Fs, basePath)
```

When a directory at `/documents/shared` is shared, `filepath.Dir("/documents/shared")` evaluates to `"/documents"`. The `BasePathFs` is then rooted at the parent directory `/documents/`, giving the share link access to **everything** under `/documents/` - not just the intended `/documents/shared/`.

This affects both `publicShareHandler` (directory listing via `/api/public/share/{hash}`) and `publicDlHandler` (file download via `/api/public/dl/{hash}/path`).

### PoC

1. Set up filebrowser with a user whose scope contains:
2.    - `/documents/shared/public-file.txt` (intended to be shared)
3.    - `/documents/secrets/passwords.txt` (NOT intended to be shared)
4.    - `/documents/private/financial.csv` (NOT intended to be shared)
2. Create a public share link for the directory `/documents/shared` (via POST `/api/share/documents/shared`)
3. Access the share link: `GET /api/public/share/{hash}`
4.    - **Expected**: Lists only contents of `/documents/shared/`
5.    - **Actual**: Lists contents of `/documents/` (parent), revealing `secrets/`, `private/`, and `shared/` directories
4. Download sibling files: `GET /api/public/dl/{hash}/secrets/passwords.txt`
5.    - **Expected**: 404 or 403 (file outside share scope)
6.    - **Actual**: 200 with file contents (sibling file downloaded successfully)
**Standalone Go test** reproducing the exact vulnerable code path with `afero.NewBasePathFs`:

```go
func TestShareScopeEscape(t *testing.T) {
    baseFs := afero.NewMemMapFs()
    afero.WriteFile(baseFs, "/documents/shared/public.txt", []byte("public"), 0644)
    afero.WriteFile(baseFs, "/documents/secrets/passwords.txt", []byte("admin:hunter2"), 0644)

    linkPath := "/documents/shared"
    basePath := filepath.Dir(linkPath) // BUG: "/documents"
    scopedFs := afero.NewBasePathFs(baseFs, basePath)

    // Sibling file is accessible through the share:
    f, err := scopedFs.Open("/secrets/passwords.txt")
    // err is nil - file accessible! Content: "admin:hunter2"
}
```

This test passes, confirming the vulnerability.

### Impact

**Unauthenticated information disclosure (CWE-200, CWE-706)**. Anyone with a public share link for a directory can:
- Browse all sibling directories and files of the shared directory
- - Download any file within the parent directory scope
- - This works without authentication (public shares) or after providing the share password (password-protected shares)
All filebrowser v2.x installations that use directory sharing are affected.

### Recommended Fix

Remove the `filepath.Dir()` call and use `link.Path` directly as the `BasePathFs` root:

```go
if file.IsDir {
    // Don't change basePath - keep it as link.Path
    filePath = ifPath
}
d.user.Fs = afero.NewBasePathFs(d.user.Fs, basePath)
```

**Affected commit**: e3d00d591b567a8bfe3b02e42ba586859002c77d (latest)
**File**: `http/public.go`, line 59

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-mr74-928f-rw69
- https://nvd.nist.gov/vuln/detail/CVE-2026-28492
- https://github.com/filebrowser/filebrowser/commit/31194fb57a5b92e7155219d7ec7273028fcb2e83
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.61.0

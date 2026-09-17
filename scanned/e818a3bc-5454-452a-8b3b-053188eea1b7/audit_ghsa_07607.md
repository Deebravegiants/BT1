# [H] Dagu: Path traversal in DAG creation allows arbitrary YAML file write outside DAGs directory

## Summary
Severity: High
Advisory: GHSA-6v48-fcq6-ff23
CVE: CVE-2026-27598
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-6v48-fcq6-ff23
Type: github-advisory

## Affected
- Go: `github.com/dagu-org/dagu` — affected >=0

## Details
The `CreateNewDAG` API endpoint (`POST /api/v1/dags`) does not validate the DAG name before passing it to the file store. While `RenameDAG` calls `core.ValidateDAGName()` to reject names containing path separators (line 273 in `dags.go`), `CreateNewDAG` skips this validation entirely and passes user input directly to `dagStore.Create()`.

In `internal/persis/filedag/store.go`, the `generateFilePath` function (line 493) checks if the name contains a path separator, and if so, resolves it via `filepath.Abs(name)` — completely ignoring the `baseDir`. This means a name like `../../tmp/pwned` will write a file to `/tmp/pwned.yaml` instead of the DAGs directory.

**Affected code:**

`internal/service/frontend/api/v1/dags.go` line 120-170 — `CreateNewDAG` handler, no call to `ValidateDAGName`

`internal/persis/filedag/store.go` line 493-498 — `generateFilePath` resolves absolute path when name contains separator

`internal/persis/filedag/store.go` line 213 — `Create` calls `generateFilePath` and writes attacker-controlled YAML content to the resolved path

**PoC:**

```
curl -X POST http://localhost:8080/api/v1/dags \
  -H "Content-Type: application/json" \
  -d '{
    "name": "../../tmp/path-traversal-proof",
    "spec": "steps:\n  - command: id > /tmp/pwned\n"
  }'
```

After this request, a file `/tmp/path-traversal-proof.yaml` will be created with the attacker-supplied content. The file will be written with the permissions of the dagu process.

An authenticated user with DAG write permissions can write arbitrary YAML files anywhere on the filesystem (limited by the process permissions). Since dagu executes DAG files as shell commands, writing a malicious DAG to the DAGs directory of another instance or overwriting config files can lead to remote code execution.

## References
- https://github.com/dagu-org/dagu/security/advisories/GHSA-6v48-fcq6-ff23
- https://nvd.nist.gov/vuln/detail/CVE-2026-27598
- https://github.com/dagu-org/dagu/commit/e2ed589105d79273e4e6ac8eb31525f765bb3ce4
- https://github.com/dagu-org/dagu
- https://pkg.go.dev/vuln/GO-2026-4542

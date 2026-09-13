# [H] goshs: WebDAV listener ignores --read-only, --upload-only, and --no-delete mode flags

## Summary
Severity: High
Advisory: GHSA-3whc-qvhv-xqjp
CVE: CVE-2026-50138
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-3whc-qvhv-xqjp
Type: github-advisory

## Affected
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.0

## Details
# WebDAV listener ignores `--read-only`, `--upload-only`, and `--no-delete` mode flags

**Ecosystem:** Go
**Package:** `goshs.de/goshs/v2` (`github.com/patrickhener/goshs`)
**Affected:** `<= v2.0.9` (every release that ships the WebDAV handler)

## Summary

When `goshs` is launched with WebDAV enabled (`-w`), the mode-restriction flags `--read-only`, `--upload-only`, and `--no-delete` are enforced only on the primary HTTP port. The WebDAV port is wired straight to `golang.org/x/net/webdav.Handler` with no equivalent guard, so an authenticated WebDAV client can `PUT`, `DELETE`, `MKCOL`, `MOVE`, and `COPY` despite the operator's stated intent.

## Details

[`httpserver/server.go:207-238`](https://github.com/patrickhener/goshs/blob/v2.0.9/httpserver/server.go#L207-L238) — the WebDAV mux registers only `IPWhitelistMiddleware`, `ServerHeaderMiddleware`, and optionally `BasicAuthMiddleware`. There is no `fs.ReadOnly || fs.UploadOnly || fs.NoDelete` check on the WebDAV path. The HTTP mux in the same file (lines 134-204) does check these flags on every state-changing route.

## Proof of concept

```bash
mkdir -p /tmp/r && echo secret > /tmp/r/x.txt
goshs -p 18000 -wp 18001 -w -ro -d /tmp/r -b admin:pw &

curl -u admin:pw -X PUT    http://localhost:18000/y.txt --data x   # 403  (HTTP enforces -ro)
curl -u admin:pw -X PUT    http://localhost:18001/y.txt --data x   # 201  (WebDAV writes anyway)
curl -u admin:pw -X DELETE http://localhost:18001/x.txt            # 204  (WebDAV deletes anyway)
curl -u admin:pw -X MKCOL  http://localhost:18001/pwned/           # 201  (WebDAV creates dir)
```

## Impact

- **Integrity** — `--read-only` and `--no-delete` are silently downgraded to "no protection" on the WebDAV port. Any WebDAV client (curl, cadaver, Windows Explorer, Finder) can overwrite/delete files.
- **Confidentiality** — `--upload-only` is also bypassed: WebDAV GET/PROPFIND still return file contents.
- **Trust** — operators using `goshs -w -ro -d /srv/case-files -b reviewer:pw` to deliver engagement artifacts believe the directory is immutable. It isn't.

## Suggested fix

Add a small `http.HandlerFunc` in front of `wdHandler` that maps WebDAV verbs to the existing mode flags:

```go
wdGuard := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodPut, "MKCOL", "MOVE", "COPY":
        if fs.ReadOnly || fs.UploadOnly { http.Error(w, "read-only", 403); return }
    case http.MethodDelete:
        if fs.ReadOnly || fs.UploadOnly || fs.NoDelete { http.Error(w, "delete disabled", 403); return }
    case http.MethodGet, "PROPFIND", "HEAD":
        if fs.UploadOnly { http.Error(w, "upload-only", 403); return }
    }
    wdHandler.ServeHTTP(w, r)
})
```

Add regression tests in `integration/functions.go` covering each mode flag × each WebDAV verb.

Reporter: Nishant Verma. Reproduced live against `goshs v2.0.9` (commit `8fc1e91`) on 2026-05-27.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-3whc-qvhv-xqjp
- https://github.com/patrickhener/goshs

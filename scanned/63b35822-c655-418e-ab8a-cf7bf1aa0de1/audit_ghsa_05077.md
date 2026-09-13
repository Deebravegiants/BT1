# [H] File Browser: Cross-user unauthorized share-link deletion via unbounded prefix match in DeleteWithPathPrefix

## Summary
Severity: High
Advisory: GHSA-5ww9-jg6q-38r7
CVE: CVE-2026-54097
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-5ww9-jg6q-38r7
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser` — affected >=0
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.6

## Details
### Summary
A low-privileged authenticated user of filebrowser (with `create` + `delete` permissions in their own isolated scope) can silently destroy share-link records belonging to any other user — including the administrator — by performing a legitimate DELETE on a file in their own directory whose logical path happens to be a byte-prefix of another user's stored `share.Link.Path`. The file contents of the victim are not exposed, but the victim's share links are irrevocably wiped.

### Details
`resourceDeleteHandler` in `http/resource.go` cleans up any share records that reference a deleted file by calling:

```go
// http/resource.go
err = d.store.Share.DeleteWithPathPrefix(file.Path)
```

`file.Path` here is the *logical* path from the URL of the deleting user's request (e.g. `/a`), not the absolute filesystem path. It is passed as-is to the bolt backend:

```go
// storage/bolt/share.go
func (s shareBackend) DeleteWithPathPrefix(pathPrefix string) error {
    var links []share.Link
    if err := s.db.Prefix("Path", pathPrefix, &links); err != nil {
        return err
    }
    for _, link := range links {
        err = errors.Join(err, s.db.DeleteStruct(&share.Link{Hash: link.Hash}))
    }
    return err
}
```
**Why the design contradicts this behavior.** `share.Link` carries a `UserID` field and the application elsewhere treats shares as per-user owned resources. `shareDeleteHandler` explicitly enforces `link.UserID != d.user.ID && !d.user.Perm.Admin → 403`. The file-deletion side-effect path is the only location that bypasses this rule.



### Impact
- Integrity: unauthorized deletion of share-link metadata belonging to arbitrary users, including administrators.
- Availability: effective denial-of-service of the share-link feature — a cooperating (or malicious) low-priv user can wipe the bulk of existing share links by iterating a short set of one- and two-character prefixes.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-5ww9-jg6q-38r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54097
- https://github.com/filebrowser/filebrowser/commit/0231b7ebdfbe77a6c54027d30c4856c3fd81ee4d
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.6

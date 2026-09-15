# [M] SiYuan: Password (protected) tier omitted in the attribute-view/database publish filter: Reader receives rows of protected documents without the password (publish mode)

## Summary
Severity: Medium
Advisory: GHSA-6mcf-g667-w3qv
Aliases: CVE-2026-72806, GO-2026-6388
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-6mcf-g667-w3qv
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723040913-768427f20f13

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72806](https://nvd.nist.gov/vuln/detail/CVE-2026-72806).

### Summary

`FilterViewByPublishAccess`, the filter `renderAttributeView` applies for Reader sessions drops rows using only the hidden/forbidden check and never checks the publish password. Its three sibling filters all check both tiers. As a result, a publish `RoleReader` (or the anonymous account when `Publish.Auth.Enable` is `false`) who has not entered a document's password still receives every database/attribute-view row bound to that password-protected document, the primary cell (title/ID) and all column values.

### Details

`FilterViewByPublishAccess` (`model/publish_access.go:290`) drops rows on the hidden/forbidden tier only:
```go
// Table (line 311), Gallery (348), Kanban (385), all identical:
if !CheckPathAccessableByPublishIgnore(bt.BoxID, bt.Path, publishIgnore) {
    row = nil   // hidden/forbidden dropped, but password NEVER checked
}
```

The three sibling filters all check both the hidden/forbidden tier and the password tier (`password == "" || CheckPublishAuthCookie(...)`):
- `FilterBlockAttributeViewKeysByPublishAccess` (line 412)
- `FilterBlockInfoByPublishAccess` (line 457)
- `FilterContentByPublishAccess` (line 474)

So the password (protected) tier is enforced everywhere except this AV/database-view filter. Table layout masks nothing; Gallery and Kanban mask only the cover, keeping the card and its non-cover values. Reachable via `renderAttributeView`, `getAttributeViewKeys`, and `renderSnapshotAttributeView`, all `CheckAuth`-only.

### Proof of Concept

Reproduced on a live instance (publish mode on 6808, anonymous Reader, no password cookie), against a password-protected document with a database/AV row.

| Check | Path | Result |
|---|---|---|
| Control | `getDoc(secretDoc)` | 🔒 placeholder, body withheld password gate works normally |
| Test | `renderAttributeView(AV)` | row leaked : `blockID=…rk7jofz`, title `secret-db-row` |
| Differential (`disable=true`) | same filter | 0 rows : hidden tier correctly enforced |
| Differential (password set) | same filter | 1 row : password tier bypassed |

Same filter, same document, same Reader: the hidden tier drops the row, the password tier leaks it isolating the omission.

### Impact

An anonymous/Reader publish user who has not supplied a protected document's password receives all attribute-view/database rows bound to that document titles, block IDs, and column values defeating the publish-password control for database views. Confidentiality-only. The hidden/forbidden tier is unaffected (correctly enforced).

### Suggested fix

Add the password check to the drop condition in all three layout branches (Table, Gallery, Kanban), mirroring the sibling filters:
```go
if !CheckPathAccessableByPublishIgnore(...) ||
   !(password == "" || CheckPublishAuthCookie(c, passwordID, password)) {
    row = nil
}
```

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-6mcf-g667-w3qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-72806
- https://github.com/siyuan-note/siyuan/commit/768427f20f13bbd8dc4effa8aa4e1d09a7741bf4
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-authentication-bypass-via-attribute-view

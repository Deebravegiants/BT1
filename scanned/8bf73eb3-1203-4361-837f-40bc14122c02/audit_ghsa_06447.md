# [M] Cloudreve: Path Traversal in WOPI PUT_RELATIVE Allows Arbitrary File Creation in Owner Account

## Summary
Severity: Medium
Advisory: GHSA-49h3-cwhj-4737
CVE: CVE-2026-55495
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-49h3-cwhj-4737
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260613023150-7968e50429ef
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary
 
Cloudreve's WOPI `PUT_RELATIVE` handler treats `X-WOPI-SuggestedTarget` as a path, not a filename. It splits the header on `/` and joins the segments onto the source file's directory with `URI.JoinRaw`, which feeds Go's `url.JoinPath`. `url.JoinPath` resolves `.`/`..` segments, so a slash-bearing target such as `a/../../evil.docx` collapses to a location outside the source file's directory. The lower-level upload path then validates only the final, already-cleaned basename (`evil.docx`), which is harmless, and checks ownership against the *resolved ancestor* — which is still the same user's drive.
 
A WOPI access token is bound to exactly one file (the route enforces `fileId == session.FileID` with a 403 otherwise). `PUT_RELATIVE` escapes that per-file scope: a token issued for one file can create (and, conditionally, overwrite) files elsewhere in the same account.

## Root cause (verified at `26b6b10`)
 
**1. Token is single-file scoped (the boundary being escaped)** — `middleware` `ViewerSessionValidation`:
 
```go
fileId := hashid.FromContext(c)
if fileId != session.FileID {           // 403 — token is bound to ONE file
    c.Status(http.StatusForbidden); c.Abort(); return
}
```
 
Route: `wopi := noAuth.Group("file/wopi", middleware.HashID(hashid.FileID), middleware.ViewerSessionValidation())`; `wopi.POST(":id", controllers.ModifyFile)` → `POST /api/v4/file/wopi/:id?access_token=<token>`.
 
**2. `PUT_RELATIVE` dispatch** — `routers/controllers/wopi.go`:
 
```go
case wopi.MethodPutRelative:            // X-WOPI-Override: PUT_RELATIVE
    err = service.PutContent(c, true)
```
 
**3. SuggestedTarget joined as a path** — `service/explorer/viewer.go`:
 
```go
fileName, _ := wopi.UTF7Decode(c.GetHeader(wopi.SuggestedTargetHeader)) // X-WOPI-SuggestedTarget
fileUriParsed, _ := fs.NewUriFromString(fileUri)
if strings.HasPrefix(fileName, ".") { /* treat as extension */ }
fileUri = fileUriParsed.DirUri().JoinRaw(fileName).String()             // <-- path join, not basename
...
subService := FileUpdateService{ Uri: fileUri }
res, err := subService.PutContent(c, lockSession)
```
 
**4. `JoinRaw` splits on `/` and normalizes via `url.JoinPath`** — `pkg/filemanager/fs/uri.go`:
 
```go
func (u *URI) Join(elem ...string) *URI {
    newUrl, _ := url.Parse(u.U.String())
    return &URI{U: newUrl.JoinPath(/* PathEscape each elem */ ...)} // JoinPath cleans ./ and ../
}
func (u *URI) JoinRaw(elem string) *URI {
    return u.Join(strings.Split(strings.TrimPrefix(elem, Separator), Separator)...)
}
```
 
`PathEscape` leaves `.` unescaped (it is in the unreserved set), so `..` segments survive into `JoinPath`, which resolves them. `URI.Name()` returns `path.Base(path.Clean(path))` — the cleaned basename.
 
**5. Upload checks ownership of the resolved ancestor and validates only the clean basename** — `pkg/filemanager/fs/dbfs/upload.go`:
 
```go
ancestor, err := f.getFileByPath(ctx, navigator, req.Props.Uri)        // URI already traversal-normalized
...
if _, ok := ctx.Value(ByPassOwnerCheckCtxKey{}).(bool); !ok && ancestor.OwnerID() != f.user.ID {
    return nil, fs.ErrOwnerOnly                                        // same-user -> passes
}
...
if err := validateNewFile(req.Props.Uri.Name(), req.Props.Size, policy); err != nil { // checks "evil.docx" only
    return nil, err
}
```
 
`validateFileName` rejects `/ \ : * ? " < > |` and bare `.`/`..` — but the traversal is already gone by the time it sees the basename.

## Validation performed
 
Independent validation against commit `26b6b10` in a clean sandbox.
 
**Source-verified (static):** the full chain confirmed verbatim — single-file-scoped token (403 on mismatch) → `PUT_RELATIVE` dispatch → `DirUri().JoinRaw(SuggestedTarget)` → `url.JoinPath` normalization → ancestor ownership check (same-user passes) → basename-only validation of the cleaned name.
 
**Dynamic (control-flow executed):** the full binary is not buildable offline here (modules behind an unreachable Go proxy, embedded frontend, DB). I built and ran a harness using the **real Go `net/url` stdlib** plus the **verbatim** `Join`/`JoinRaw`/`DirUri`/`Path`/`Name`/`PathEscape`/`shouldEscape` and the `validateFileName` gate, driving the same transformation `PUT_RELATIVE` performs. Source = `cloudreve://my/folder/current.docx`:
 
```
SuggestedTarget            resolved URI                          final basename   validator
"copy.docx"                cloudreve://my/folder/copy.docx       "copy.docx"      ACCEPT
"a/../../evil.docx"        cloudreve://my/evil.docx              "evil.docx"      ACCEPT   <- ESCAPED to /
"a/../../../top.docx"      cloudreve://my/top.docx               "top.docx"       ACCEPT   <- ESCAPED to /
"sub/evil.docx"            cloudreve://my/folder/sub/evil.docx   "evil.docx"      ACCEPT   <- different subdir
".pdf"                     cloudreve://my/folder/current.pdf     "current.pdf"    ACCEPT
"a%2f..%2f..%2fenc.docx"   cloudreve://my/folder/a%252f..%252f.. "a%2f..%2f..%2f" ACCEPT   (NO escape)
```
 
The headline payload `a/../../evil.docx` deterministically resolves to `cloudreve://my/evil.docx` (account root) with a clean, accepted basename. Output matches the original audit probe exactly. Honest caveat: a leading non-`..` segment (e.g. `a/`) is required to prime the join; a single `../evil.docx` does not cleanly escape, and **URL-encoded separators (`%2f`) do not traverse** through this path (they are re-escaped into one literal segment). Only literal `/` separators work.
 
**Confidence tier: source-verified + control-flow dynamically reproduced (no full live HTTP write against a deployed instance).**
 
**Deduplication:** no existing CVE/GHSA matches. Known Cloudreve advisories are CVE-2022-32167 (XSS, v1–v3.5.3) and CVE-2026-25726 (weak-PRNG ATO, instances initialized < v4.10.0) — both unrelated. `SECURITY.md` lists "user permissions" as high-impact and in scope for all 4.x, so this qualifies as a vulnerability under the project's own policy.
 
## Steps to reproduce
 
**Setup:** user owns `cloudreve://my/folder/current.docx`; open it in the WOPI editor to obtain `<token>` (the session is bound to that file's ID).
 
1. Send the crafted `PUT_RELATIVE`:
   ```
   POST /api/v4/file/wopi/<file-id>?access_token=<token> HTTP/1.1
   Host: target
   X-WOPI-Override: PUT_RELATIVE
   X-WOPI-SuggestedTarget: <UTF-7 of "a/../../evil.docx">
   Content-Type: application/octet-stream
 
   <file bytes>
   ```
2. Cloudreve rewrites the target from `cloudreve://my/folder/current.docx` to `cloudreve://my/evil.docx`, validates the basename `evil.docx` (passes), and writes the content.
**Expected:** the target is rejected or constrained to the source file's directory.
**Actual:** a file is written at the account root, outside the token's single-file scope.
 
## Impact
 
A WOPI access token scoped to one file can write files to other locations in the same user's account. A malicious or compromised WOPI integration (or a leaked token) can plant or, conditionally, overwrite files at attacker-chosen paths the account owns, defeating the per-file scoping the WOPI session is meant to enforce. Confined to the session user's account (not cross-user).
 
## Remediation
 
- Treat `X-WOPI-SuggestedTarget` (and `X-WOPI-RequestedName`) as a **filename**, not a path: reject `/`, `\`, dot segments, and percent-encoded separator variants before joining.
- Prefer `DirUri().Join(sanitizedBaseName)` over `JoinRaw`, and after constructing the target URI assert it is a direct child of the source file's directory.
- Add regression tests for `a/../../evil.docx`, `sub/evil.docx`, and encoded-separator variants.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-49h3-cwhj-4737
- https://github.com/cloudreve/cloudreve/commit/7968e50429efab40ffa8f57fecdfbd5a73d23630
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.17.0

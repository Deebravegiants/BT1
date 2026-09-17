# [M] SiYuan: Static-file routes bypass the publish-access controls enforced on the REST API, exposing templates, snippets and export artifacts to anonymous readers

## Summary
Severity: Medium
Advisory: GHSA-fgmr-7w36-9qfq
Aliases: CVE-2026-72796, GO-2026-6423
Ecosystem: Go
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-fgmr-7w36-9qfq
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260725122641-34be6c0bb073

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72796](https://nvd.nist.gov/vuln/detail/CVE-2026-72796).

### Summary

Several static-file routes in the server mux (`kernel/server/serve.go`) are registered with `CheckAuth` only and serve directories directly, without the publish-access checks, sensitive-path blocklist, or `refuseToAccess` rules that the REST API applies to the same data. They are therefore reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`.

Most notably, `/templates/` serves `data/templates` a directory the REST file API explicitly refuses to serve to non-administrators.

### Details

| Route | Registration | Guard | Exposed to a reader |
|---|---|---|---|
| `/templates/*` (line 424) | `Group("/templates/", model.CheckAuth).Static("", data/templates)` | none beyond path cleaning | the templates directory |
| `/snippets/*` (line 434) | `CheckAuth` | blocks only `conf.json` | any snippet's JS/CSS content by name |
| `/widgets/`, `/plugins/`, `/emojis/` (409/414/419) | `Group(CheckAuth).Static(dir)` | none | whole directory trees |
| `/export/*` (line 320) | `Group("/export/", CheckAuth)` | traversal, sensitive-path and DEK guards: **no publish check** | export artifacts (PDF/HTML/DOCX/CSV) |

**`/templates/` directly contradicts an existing control.** The REST file path runs `refuseToAccess` (`kernel/api/file.go:551-553`), which explicitly returns 403 for `data/templates/` to non-administrators the project has already decided readers must not read templates. The `/templates/` static route serves that same directory to any `RoleReader`, with no `IsSensitivePath` check, no publish-access check, and no `refuseToAccess`. Templates are user-authored Markdown documents containing template/Sprig syntax and are not covered by publish-access controls. `gin`'s `.Static` disables directory listing, so a filename is required but the contradiction with `refuseToAccess` is the defect.

**`/export/` versus `/assets/`.** `/assets/*path` (line 692) correctly gates non-administrators via `CheckAbsPathAccessableByPublishAccess`, plus `IsSensitivePath` and encrypted-asset handling. `/export/` carries traversal, sensitive-path and DEK guards but no publish-access check, so a reader can retrieve export artifacts of arbitrary documents, including private ones. Artifact naming is mixed, some use a random export ID, but code and CSV exports use the document name (`export/code/<name>`, `export/csv/<name>/<name>.csv`), which a reader can derive from `listDocsByPath` titles while the artifact exists. This path is therefore conditional.

**Confirmed correctly gated, for contrast:** `/assets/*` (publish-gated), `/history/*` and `/repo/diff/*` (`CheckAdminRole`), `/debug/pprof/*` (disabled in production builds), `/public/` (intentionally public).

All four routes above were verified to carry `CheckAuth` only, no `CheckReadonly`, no `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808), anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account.

**Templates: served despite the REST API refusing them:**
```
GET http://127.0.0.1:6808/templates/<template-file>.md
→ 200, template content
```
The equivalent REST request is refused:
```
POST http://127.0.0.1:6808/api/file/getFile
{"path":"data/templates/<template-file>.md"}
→ 403 (refuseToAccess)
```
The same reader session obtains the file through the static route.

**Snippets:**
```
GET http://127.0.0.1:6808/snippets/<snippet-name>.js
→ 200, snippet source
```

**Export artifacts (conditional on a predictable name while the artifact exists):**
```
GET http://127.0.0.1:6808/export/csv/<doc-name>/<doc-name>.csv
→ 200, exported content of a document the reader has no publish access to
```

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read user-authored template documents that the REST API explicitly withholds from non-administrators, snippet source (JS/CSS), and the contents of the widgets, plugins and emoji directories. Where an export artifact exists under a derivable name, they can additionally retrieve exported content of documents outside their publish scope. Confidentiality-only.

### Suggested fix

Apply the same treatment these routes' REST counterparts already receive: for non-administrator roles, enforce publish-access scoping plus `IsSensitivePath` and the `refuseToAccess` blocklist on the static routes, mirroring `/assets/*`. Alternatively, block `/templates/`, non-public `/snippets/`, and `/export/` for reader roles entirely.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-fgmr-7w36-9qfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72796
- https://github.com/siyuan-note/siyuan/commit/34be6c0bb0739d5b8e99ecc0cbfb474abb16230d
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-access-control-bypass-via-static-routes

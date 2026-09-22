# [M] SiYuan: Tag labels from password-protected documents are returned to readers who have not entered the password

## Summary
Severity: Medium
Advisory: GHSA-mp7r-57w4-5qm3
Aliases: CVE-2026-72792, GO-2026-6427
Ecosystem: Go
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-mp7r-57w4-5qm3
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260726002639-4515fa257cfa

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72792](https://nvd.nist.gov/vuln/detail/CVE-2026-72792).

### Summary

`/api/tag/getTag` filters its results for reader roles through `FilterTagsByPublishIgnore`, which checks only the *visible* publish tier. Documents that are published but password-protected pass that check, so a reader who has never entered a document's publish password receives every tag label used inside it, together with occurrence counts.

The project has already treated this exact tier mismatch as a vulnerability on a sibling path: commit `82e9ded42` ("Enforce publish access for graph nodes") moved the graph endpoint off the visible-only filter and onto a password-aware one. `FilterTagsByPublishIgnore` was not upgraded alongside it.

### Details

| Item | Detail |
|---|---|
| Route | `kernel/api/router.go:194` `POST /api/tag/getTag` → `model.CheckAuth` → `getTag` |
| Middleware | `CheckAuth` only: no `CheckReadonly`, no `CheckAdminRole` |
| Guard | Present but at the wrong tier: visible-only, no password check |
| Exposed | Every tag label (`#label#` text) and its occurrence count inside password-protected but visible documents |

**The tier mismatch.** For reader roles, `getTag` filters via:

```go
publishIgnore := GetInvisiblePublishAccess(publishAccess)
tags = FilterTagsByPublishIgnore(publishIgnore, tags)
```

`FilterTagsByPublishIgnore` counts a label if `CheckPathAccessableByPublishIgnore(span.Box, span.Path, publishIgnore)` holds, then reads `label := util.UnescapeHTML(span.Content)`.

`CheckPathAccessableByPublishIgnore` (`kernel/model/publish_access.go:183`) consults the invisible set only. It returns true for any visible document, including one carrying a publish password. The project's complete gate is `checkBlockTreeAccessableByPublishAccess` (`kernel/model/publish_access.go:225`), which ANDs that same visibility test with `password == "" || CheckPublishAuthCookie(...)`. The tag filter implements the first half and omits the second.

The disclosed value is user-authored content, not a structural identifier: `span.Content` is the tag text an author wrote inside the document project codenames, personal names, client names, subject matter and the accompanying count reveals how heavily each appears.

**Established as a defect by the project's own remediation.** Commit `82e9ded42` replaced the graph endpoint's visible-only `FilterGraphByPublishIgnore` with a filter that additionally resolves the document's publish password and validates `CheckPublishAuthCookie`. The reasoning that motivated that change applies unchanged here: same input shape, same visible-only body, same class of leaked material. `FilterTagsByPublishIgnore` retains the pre-fix pattern.

**Verified unfixed.** At `v3.7.4-alpha.1`, `getTag` still calls `FilterTagsByPublishIgnore`, and that function's body still tests only `CheckPathAccessableByPublishIgnore`. No commit on the development branch touches `kernel/api/tag.go` or the tag filter (`git log` and `git log -S` both empty over that range).

**Scope note on the remaining visible-only call sites.** Two further consumers of the `*ByPublishIgnore` tier were reviewed and are not claimed as vulnerabilities in this report: `listDocsByPath` (`kernel/model/filetree.go:1160`), which exposes document titles and is plausibly intentional for navigation, and the identifier-only filter, which returns no authored content. They are noted because the visible-only tier is now a repeated source of defects, and an audit of every `*ByPublishIgnore` call site is the durable remedy rather than a third individual patch.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); a published document that carries a publish password and contains at least one tag; a reader session that has not authenticated to that document.

```
POST http://127.0.0.1:6808/api/tag/getTag
{}

→ 200
   The returned tag tree includes labels sourced from the password-protected
   document, with counts, despite the session holding no publish auth cookie
   for it.
```

Differential check: request the document itself through a password-gated endpoint with the same session and observe that access is refused, while its tag labels remain present in the `getTag` response.

### Impact

An anonymous reader in publish mode or any publish `RoleReader` enumerates the tag vocabulary of documents they are not authorized to open, along with usage counts. Tags are author-written free text, so this discloses subject matter, names and internal terminology from documents whose contents the publish password was configured to protect. Confidentiality-only.

### Suggested fix

Replace `FilterTagsByPublishIgnore` with a password-aware filter mirroring the one introduced in `82e9ded42` for graph nodes: resolve each span's document password via `GetPathPasswordByPublishAccess` and require `CheckPublishAuthCookie` before the label is counted, in addition to the existing visibility test. More durably, audit every remaining `*ByPublishIgnore` call site against `checkBlockTreeAccessableByPublishAccess` the visible-only tier has now produced this defect on at least two separate endpoints.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-mp7r-57w4-5qm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-72792
- https://github.com/siyuan-note/siyuan/commit/4515fa257cfae2db0a43844c61de8ef1ac853796
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-tag-api

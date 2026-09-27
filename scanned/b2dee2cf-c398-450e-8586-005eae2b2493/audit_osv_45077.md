# [M] SiYuan: Missing publish-access filter on the HPath/path-resolution endpoints discloses the private document tree to anonymous readers

## Summary
Severity: Medium
Advisory: GHSA-5w7r-f4cg-rqq7
Aliases: CVE-2026-72799, GO-2026-6412
Ecosystem: Go
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-5w7r-f4cg-rqq7
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724112156-5bae0926b896

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72799](https://nvd.nist.gov/vuln/detail/CVE-2026-72799).

### Summary

Five filetree endpoints resolve arbitrary document IDs and paths with no publish-access check of any kind. All are `CheckAuth`-only, so they are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. An anonymous reader can map the complete private document tree every notebook, folder, and document title, and which notebook holds each document for documents marked hidden, password-protected, or publish-forbidden, and can resolve titles to document IDs.

### Details

None of the following handlers invokes `IsReadOnlyRoleContext`, `CheckBlockIdAccessableByPublishAccess`, or `CheckPathAccessableByPublishIgnore`:

| Endpoint | Returns | Discloses |
|---|---|---|
| `getFullHPathByID` (router 159) | `GetFullHPathByID(id)` | full title path including notebook, e.g. `/MySecretNotebook/Confidential/Q3 Layoffs Plan` |
| `getHPathByID` (router 157) | `GetHPathByID(id)` | document-relative title path |
| `getPathByID` (router 158) | `{path, notebook}` | which notebook a document lives in, plus its `.sy` storage path |
| `getIDsByHPath` (router 160) | `GetIDsByHPath(path, notebook)` | title-path → document-ID enumeration |
| `getHPathByPath` (router 155) | HPath from a storage path | title path from a storage path |

Each accepts an arbitrary ID or HPath and resolves it identically for hidden, publish-forbidden, and password-protected documents.

This enables two operations for an unauthenticated caller:
1. **Map the private document tree**: `getFullHPathByID` and `getPathByID` yield every notebook/folder/document title and its containing notebook.
2. **Resolve titles to IDs**: `getIDsByHPath` converts a known or guessed title path into document IDs, which are the required input for other block-read endpoints.

Document titles and HPaths are precisely the block metadata that the project's block-metadata restriction (commit `ffde3b21e`) set out to protect; that change gated `getBlockInfo`, `getDocInfo`, and `getDocsInfo` but left this entire path-resolution family open.

**Guarded-sibling asymmetry.** `getRecentDocs` (`FilterRecentDocsByPublishAccess`), `getCriteria` (`FilterCriteriaByPublishAccess`), and `getLocalStorage` (`FilterLocalStorageByPublishAccess`) all filter document references for reader sessions. The codebase clearly publish-scopes reader-visible metadata elsewhere; these five endpoints do not.

Verified at `origin/master` (`eef105683`): all five handler bodies contain no publish-access call; the storage-family siblings contain their filters; all five routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A document exists in a notebook marked publish-forbidden or password-protected.

**Resolve a private document's full title path:**
```
POST http://127.0.0.1:6808/api/filetree/getFullHPathByID
{"id":"<DOC_ID>"}
→ /MySecretNotebook/Confidential/Q3 Layoffs Plan
```

**Identify its notebook and storage path:**
```
POST http://127.0.0.1:6808/api/filetree/getPathByID
{"id":"<DOC_ID>"}
→ {"path":"/....sy","notebook":"<BOX_ID>"}
```

**Enumerate IDs from a title path:**
```
POST http://127.0.0.1:6808/api/filetree/getIDsByHPath
{"path":"/Confidential","notebook":"<BOX_ID>"}
→ document IDs under a folder the reader cannot otherwise access
```

Each returns data for documents excluded from publishing; no password or membership is required.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can enumerate the complete private document structure: notebook names, folder hierarchy, and document titles for content the administrator marked hidden, password-protected, or excluded from publishing. Document titles alone are frequently sensitive (project names, personnel actions, client identifiers). The ID-resolution direction additionally supplies valid document IDs, removing the "attacker must know an ID" precondition for other block-read endpoints. Confidentiality-only.

### Suggested fix

For `IsReadOnlyRoleContext` sessions, gate each of the five handlers with `CheckBlockIdAccessableByPublishAccess` (or restrict resolution to publish-visible documents), mirroring the treatment already applied in `getRecentDocs`, `getCriteria`, and `getLocalStorage`.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-5w7r-f4cg-rqq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72799
- https://github.com/siyuan-note/siyuan/commit/5bae0926b896eaff0bc5cc6a75d421c2d161a806
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-path-resolution

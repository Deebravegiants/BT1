# [M] SiYuan: Notebook name, document count, size and timestamps are returned for any notebook, including notebooks hidden from readers, by /api/notebook/getNotebookInfo

## Summary
Severity: Medium
Advisory: GHSA-74pj-6g7r-j55c
Aliases: CVE-2026-72790, GO-2026-6431
Ecosystem: Go
Published: 2026-09-08
Source: https://osv.dev/vulnerability/GHSA-74pj-6g7r-j55c
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260726005141-9edb321eb451

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72790](https://nvd.nist.gov/vuln/detail/CVE-2026-72790).

### Relationship to GHSA-8x84-r2ff-h8pq (please read first)

`getNotebookInfo` is named in the earlier advisory GHSA-8x84-r2ff-h8pq, in its remediation section, which asked for reader filtering on both `getNotebookConf` and `getNotebookInfo`. Commit `3bc014c7d` applied that filtering to `getNotebookConf` only.

That advisory grouped `getNotebookInfo` under `BoxCrypt`, and `getNotebookInfo` never returns `BoxCrypt`. Anyone checking the handler for key material would correctly find none and move on. This report corrects that characterisation and states what the handler actually discloses, which is notebook metadata rather than key material. If you would prefer this tracked as a follow-up on the original advisory rather than separately, that is entirely reasonable.

### Summary

`/api/notebook/getNotebookInfo` is registered with `CheckAuth` only and applies no authorization check of any kind. Given a notebook identifier, it returns that notebook's author-written name, document count, total size and creation and modification timestamps. It does so for every notebook the server has loaded, including notebooks that `lsNotebooks` deliberately withholds from readers because they are closed or not publish-visible.

### Details

| Item | Detail |
|---|---|
| Route | `kernel/api/router.go:123` `POST /api/notebook/getNotebookInfo` → `model.CheckAuth` → `getNotebookInfo` |
| Middleware | `CheckAuth` only, no `CheckReadonly`, no `CheckAdminRole` |
| Guard in handler | None. `IsReadOnlyRoleContext`, `publishAccess`, `Visible` and `Closed` all return zero matches |
| Exposed | `BoxInfo{ID, Name, DocCount, Size, HSize, Mtime, CTime, HMtime, HCtime}` |
| Affected refs | `eef105683` (v3.7.3, master HEAD) and `v3.7.4-alpha.1`, handler identical on both |

**The handler.** It validates `boxID` against the ID pattern, calls `box := model.Conf.Box(boxID)`, returns a not-found response if that is nil, and otherwise returns `box.GetInfo()` unmodified. `GetInfo()` (`kernel/model/box.go:470`) walks the notebook's files and returns the metadata listed above. There is no ownership check and no publish-access check anywhere on the path.

The nil branch is also a minor existence oracle: a valid-format identifier that names no loaded notebook is distinguishable from one that does.

**Guarded sibling.** `lsNotebooks`, the notebook lister, is also reader-reachable and does filter. For read-only roles it skips any notebook where `notebook.Closed` holds, and skips any notebook whose publish-access entry has `!item.Visible`. The codebase therefore intends closed and non-published notebooks to be invisible to readers. `getNotebookInfo` returns their name and statistics to any reader who supplies the identifier.

**Precedent.** GHSA-f2rw-w22v-54vh restricted `getEncryptedNotebookStatus`, which disclosed encrypted-notebook names and lock state, to administrators. `getNotebookInfo` is the non-encrypted analogue, disclosing regular notebook names and statistics including for notebooks outside the reader's publish scope, and was not restricted.

**Reachability, stated precisely, because it differs by branch.**

On v3.7.3 a reader can obtain the identifier of a notebook they cannot see, by chaining two endpoints that are currently ungated on that branch. `getBlockDefIDsByRefText` returns block and document identifiers workspace-wide, including from hidden notebooks. `getPathByID` then returns the owning notebook identifier for any such block, in its `notebook` field. `getFullHPathByID` additionally discloses the notebook name directly. The chain requires no special conditions beyond a reference text that occurs somewhere in the workspace.

On the development branch those sources are already closed. `getPathByID` now gates through `CheckBlockIdMetadataAccessableByPublishAccessInBox`, `getIDsByHPath` through `filterFileTreeBlockIDsByPublishDiscoverability`, and `getBlockDefIDsByRefText` and `getFullHPathByID` are likewise gated. Notebook identifiers are a fourteen-digit timestamp plus seven random characters, and `Conf.Box(boxID)` returns non-nil only for loaded notebooks, so guessing is not practical. A reader-reachable route on the development branch that yields the identifier of a hidden notebook was not found.

So on the development branch this is defence in depth rather than a live path. It is reported because the handler itself remains unguarded on both branches, and because closing it removes any dependence on those identifier sources staying gated in future.

### Proof of Concept

Precondition: publish mode enabled (default port 6808), anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A notebook that is closed or not publish-visible. Steps 1 and 2 apply to v3.7.3; on the development branch, start at step 3 with a known identifier.

Step 1, obtain block identifiers workspace-wide:

```
POST http://127.0.0.1:6808/api/block/getBlockDefIDsByRefText
{"anchor":"<a word likely to occur anywhere in the workspace>"}

→ 200, block and document identifiers including ones inside hidden notebooks
```

Step 2, resolve one to its owning notebook:

```
POST http://127.0.0.1:6808/api/filetree/getPathByID
{"id":"<identifier from step 1>"}

→ 200, the notebook field carries the hidden notebook's boxID
```

Step 3, read the notebook's metadata:

```
POST http://127.0.0.1:6808/api/notebook/getNotebookInfo
{"notebook":"<boxID from step 2>"}

→ 200, returns name, docCount, size, hSize, mtime, ctime, hMtime, hCtime
   for a notebook that lsNotebooks does not return to this same session
```

The differential is the point: call `lsNotebooks` with the same session and confirm the notebook is absent from the list, then call `getNotebookInfo` and receive its name and statistics.

### Impact

An anonymous reader in publish mode, or any publish `RoleReader`, can read the author-written name, document count, total size and activity timestamps of notebooks that are closed or not published, which are exactly the notebooks the notebook lister withholds from them. Notebook names are free text chosen by the author and routinely describe their contents. Document count and size indicate scale, and the modification timestamp reveals recent activity in a workspace area the reader has no access to. Confidentiality only, with no integrity or availability impact, and no document content is disclosed.

### Suggested fix

Apply the same filtering `lsNotebooks` already performs. When `IsReadOnlyRoleContext(c)` holds, return the not-found response unless the notebook is publish-visible and not closed, before calling `GetInfo()`. This is the reader filtering the earlier advisory's remediation section requested for this handler.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-74pj-6g7r-j55c
- https://nvd.nist.gov/vuln/detail/CVE-2026-72790
- https://github.com/siyuan-note/siyuan/commit/9edb321eb451db445f3c824380e1993c3df0fc16
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-getnotebookinfo

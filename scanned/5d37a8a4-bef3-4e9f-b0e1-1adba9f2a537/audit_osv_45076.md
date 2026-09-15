# [M] SiYuan: Missing publish-access filter on getAttributeViewKeysByID discloses database column schema, plus two unscoped block-ID enumeration oracles (publish mode)

## Summary
Severity: Medium
Advisory: GHSA-5fhr-f75j-8wr9
Aliases: CVE-2026-72800, GO-2026-6395
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-5fhr-f75j-8wr9
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724103335-f36331956ae9

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72800](https://nvd.nist.gov/vuln/detail/CVE-2026-72800).

### Summary

`POST /api/av/getAttributeViewKeysByID` returns a database's full column schema with no publish-access filtering, while its sibling `getAttributeViewKeys` applies the filter for reader sessions. Two further endpoints, `getBlockDefIDsByRefText` and `getBlockRelevantIDs` return workspace-wide block IDs with no publish scoping. All three are `CheckAuth`-only, so they are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`.

### Details

**(a) `getAttributeViewKeysByID`: ungated column-schema disclosure**

The entire handler (`kernel/api/av.go`, router line 548):
```go
ret.Data = model.GetAttributeViewKeysByID(avID, keyIDs...)   // no publish gate
```

With an empty `keyIDs`, `GetAttributeViewKeysByID` calls `av.ParseAttributeView(avID)` and returns every column's `*av.Key`:

| Field | Discloses |
|---|---|
| `Name`, `Desc` | column title and user-authored description |
| `Options` | the full single/multi-select vocabulary and colours (e.g. status labels such as "Fired", "Confidential") |
| `Template` | the column's Sprig template expression — logic and field references |
| `Relation` | the target `avID`, allowing pivot to another database |
| `Rollup`, `NumberFormat`, date config | further schema |

**Guarded-sibling asymmetry, same file:** `getAttributeViewKeys` (router line 526) runs `FilterBlockAttributeViewKeysByPublishAccess(...)` when `IsReadOnlyRoleContext`. `getAttributeViewKeysByID` applies nothing. A reader who knows an `avID` — trivially harvested from the `data-av-id` attribute of any published document embedding a database obtains the schema of any database in the workspace, including those whose host documents are hidden, password-protected, or publish-forbidden. `Relation` targets allow walking to sibling databases.

**(b) Two unscoped block-ID enumeration oracles**

Both `CheckAuth`-only with no publish gate. Neither returns content of its own, but both yield valid block IDs that other endpoints turn into content:

- `getBlockDefIDsByRefText` (router line 237) → `GetBlockDefIDsByRefText(anchor)` returns the block IDs, workspace-wide and including private documents, whose reference/anchor text equals a caller-supplied string: a ref-text → ID oracle.
- `getBlockRelevantIDs` (router line 274) → `GetBlockRelevantIDsInBox(id, <notebook from request>)` returns parent/previous/next block IDs and traverses decrypted encrypted-notebook structure while the notebook is unlocked, a tree-walk oracle.

Verified at `origin/master` (`eef105683`): all three handler bodies contain no publish-access, publish-ignore, or readonly-role check; all three routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A database exists whose host document is publish-forbidden or password-protected.

**(a) Column schema of any database:**
```
POST http://127.0.0.1:6808/api/av/getAttributeViewKeysByID
{"avID":"<AV_ID>"}
```
Returns every column's key object names, descriptions, select vocabularies, template expressions, and `Relation` target `avID`s for a database whose host document the reader may not access.

**Control:** the sibling `getAttributeViewKeys` with the same `avID` returns filtered results for the same reader session, confirming the boundary is enforced there and omitted here.

**(b) ID oracles:**
```
POST http://127.0.0.1:6808/api/block/getBlockDefIDsByRefText
{"anchor":"<known ref text>"}
→ block IDs workspace-wide, including blocks in private documents

POST http://127.0.0.1:6808/api/block/getBlockRelevantIDs
{"id":"<BLOCK_ID>","notebook":"<BOX_ID>"}
→ parent/previous/next block IDs; traverses encrypted-notebook structure when unlocked
```

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read the complete column schema of any database in the workspace, including column descriptions, select-option vocabularies (which frequently encode sensitive category labels), template logic, and relation targets that permit pivoting to further databases regardless of whether the host document is hidden, password-protected, or excluded from publishing.

The two enumeration endpoints additionally supply valid block IDs across the publish boundary, including from encrypted notebooks while unlocked. This removes the "attacker must already know a valid ID" precondition from other block-read endpoints, converting ID knowledge into content disclosure. Confidentiality-only.

### Note

getAttributeViewKeysByID is a distinct handler from getAttributeView; although column definitions also appear within the latter's response payload, a fix applied to one handler does not remediate the other, and getAttributeViewKeysByID has its own filtered sibling (getAttributeViewKeys) demonstrating the intended treatment.

### Suggested fix

- Gate `getAttributeViewKeysByID` with `FilterBlockAttributeViewKeysByPublishAccess`, mirroring `getAttributeViewKeys`.
- Scope `getBlockDefIDsByRefText` and `getBlockRelevantIDs` to publish-accessible blocks for reader sessions, and ensure the `*InBox` traversal path applies the same check before walking encrypted-notebook structure.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-5fhr-f75j-8wr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-72800
- https://github.com/siyuan-note/siyuan/commit/931ba693375ea9877b2ef74f9bfb632fad5bab3f
- https://github.com/siyuan-note/siyuan/commit/f36331956ae98fc5358f8f93bf1da3427221edf3
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-unfiltered-api

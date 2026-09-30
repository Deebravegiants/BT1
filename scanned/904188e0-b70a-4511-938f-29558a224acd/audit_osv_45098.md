# [M] SiYuan: Cross-boundary metadata disclosure via getBlockInfo (publish mode): reader-reachable document title/root info for publish-forbidden docs; sibling getDocInfo is filtered

## Summary
Severity: Medium
Advisory: GHSA-pm3w-vxp9-ccwc
Aliases: CVE-2026-68585, GO-2026-6384
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-pm3w-vxp9-ccwc
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260721014951-ffde3b21eca4

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-68585](https://nvd.nist.gov/vuln/detail/CVE-2026-68585).

### Summary

The `/api/block/getBlockInfo` endpoint returns document root metadata including the document title (`rootTitle`) for a block in a publish-forbidden document, with no publish-access check. Its sibling `/api/block/getDocInfo` applies the publish-access filter, `getBlockInfo` does not. Both are gated by `CheckAuth` only, so `getBlockInfo` is reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`.

### Details

The list/info side of this API is filtered while the block-info twin is not the asymmetry indicates an oversight rather than intended behavior:

| Endpoint | Returns | Publish-access filter | Route |
|---|---|---|---|
| `getDocInfo` | document info/metadata | present | `CheckAuth` |
| `getBlockInfo` | `box, path, rootID, rootTitle, rootChildID, rootIcon` | none | `CheckAuth` |

`getBlockInfo` takes a caller-supplied block ID, validates only its format, and returns the containing document's root metadata including `rootTitle` (the document title) with no `IsReadOnlyRoleContext` / publish-access check. Because `getDocInfo` performs the filtering for equivalent data, the boundary is clearly meant to apply here; `getBlockInfo` omits it.

### Proof of Concept

Reproduced on a local instance (SiYuan running locally, publish mode enabled on port 6808, publish Basic Auth disabled). Setup: a publish-forbidden document `D` whose title is a unique marker, containing a block `BLOCKID`.

**1. Mark the document publish-forbidden (admin action):**
```
POST http://127.0.0.1:6806/api/filetree/setPublishAccess
Authorization: Token <admin-token>
{"id":"DOC","visible":false,"password":"","disable":true}
```

**2. Disclosure: the block-info endpoint returns the forbidden doc's title (anonymous, port 6808):**
```
POST http://127.0.0.1:6808/api/block/getBlockInfo
{"id":"BLOCKID"}
```
Returns HTTP 200 with `data.rootTitle` set to the publish-forbidden document's title, along with `box`, `path`, `rootID`, and `rootIcon`. This document's title is not returned by the reader-facing filtered paths.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read the title and root metadata (notebook, path, root ID, icon) of a publish-forbidden document by supplying a block ID from it. This discloses the existence, title, and location of documents an administrator marked as excluded from publishing.

**Precondition and scope (stated honestly):** the request requires a block ID from the target document; this endpoint does not enumerate arbitrary documents. The disclosure is limited to document metadata, title, notebook, path, root ID, icon — not the document body. Block IDs for forbidden documents are obtainable from other `CheckAuth`-only endpoints that lack the publish-access filter (reported separately). Impact is confidentiality-only, limited to metadata; no content body, no modification. Encrypted notebooks are out of scope.

### Suggested fix

Apply the same publish-access check `getDocInfo` uses to `getBlockInfo` before returning root metadata, resolve the block's document and enforce `IsReadOnlyRoleContext` / the publish-access filter, consistent with the sibling endpoint.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-pm3w-vxp9-ccwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-68585
- https://github.com/siyuan-note/siyuan/commit/ffde3b21eca49ae98828747ca126581a553cce8b
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-metadata-disclosure-via-getblockinfo

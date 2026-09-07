# [M] Gitea: GHSA-8fwc-qjw5-rvgp ClearRepoWatches fix not applied to API EditRepo path — sister code path retains stale watches on public->private

## Summary
Severity: Medium
Advisory: GHSA-q423-49rw-g9mh
CVE: CVE-2026-58510
CWE: CWE-200, CWE-281, CWE-359
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-q423-49rw-g9mh
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

GHSA-8fwc-qjw5-rvgp ("Gitea may send release notification emails for private repositories to users whose access has been revoked", fix in PR #36319 / commit 8a98ac22) added `repo_model.ClearRepoWatches` as a defense for the state transition public→private. The cleanup was wired into `services/repository/repository.go::MakeRepoPrivate` only. The sister helper `services/repository/repository.go::updateRepository` — which is the function used by the API path `PATCH /api/v1/repos/{owner}/{repo}` — was not patched and still calls `ClearRepoStars` only.

As a result, when a public repository is flipped to private via the REST API (rather than via the web Settings → Danger Zone UI), the watch records persist. Affected users can:

- See the now-private repository in `GET /api/v1/user/subscriptions?private=true` along with its full `Repository` JSON (description, default branch, language, fork status, counts, mirror metadata, license list, etc.) — even though they have no access to the repository.
- Have their stale watch records re-leak content through any future notification path that does not include the send-time `CheckRepoUnitUser` check that was added to `services/mailer/mail_release.go`.
- Inflate the visible `NumWatches` counter on the repository.

## Severity

Medium — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N`

Same impact class as the original GHSA-8fwc-qjw5-rvgp (which was classified Medium). The send-time mail filter added in the same PR mitigates the release-content disclosure vector. The residual leak is repo metadata via the subscriptions endpoint and stale watcher counts.

CWE-281 (Improper Preservation of Permissions), CWE-359 (Exposure of Private Personal Information), CWE-200 (Exposure of Sensitive Information).

## Affected Versions

Every release starting from v1.25.4 (the release shipping the original GHSA-8fwc-qjw5-rvgp fix) through HEAD (master @ `ef801bb6`, 2026-05-16). The follow-up refactor in commit `943ff752` (PR #36959, 2026-03-24) which merged `MakeRepoPublic`+`MakeRepoPrivate` did not propagate the `ClearRepoWatches` call to `updateRepository`.

## Affected Component

- `services/repository/repository.go:240-302` — `func updateRepository(ctx, repo, visibilityChanged bool)`, the sister helper called via the API path. Clears stars on line 273 but never calls `ClearRepoWatches`.
- `routers/api/v1/repo/repo.go::Edit` (line 573) → `updateBasicProperties` (line 678-697) → `repo_service.UpdateRepository(ctx, repo, visibilityChanged)` (line 726) — the API path that exercises the sister helper.

## Steps to Reproduce

The bug is observable purely from static analysis; the live PoC is straightforward.

1. Start a Gitea instance at any release from v1.25.4 onwards (verified static at HEAD `ef801bb6`).

2. Create users `A` (org admin) and `B` (member). Create a public repository `A/proj`. As `B`, watch the repo:
   ```
   curl -u B:<token> -X PUT "https://gitea.example.com/api/v1/repos/A/proj/subscription"
   ```

3. As `A`, flip the repo to private via the REST API (not via the web UI):
   ```
   curl -u A:<token> -X PATCH "https://gitea.example.com/api/v1/repos/A/proj" \
        -H 'Content-Type: application/json' \
        -d '{"private": true}'
   ```

4. As `B`, list `B`'s watched repos with `private=true`:
   ```
   curl -u B:<token> "https://gitea.example.com/api/v1/user/subscriptions"
   ```

   The now-private repo `A/proj` is returned in `B`'s subscription list, with the full `Repository` payload — including `description`, `default_branch`, `language`, `topics`, `license`, fork/branch/issue/release counts, etc.

5. Compare with the web-UI path (which IS patched). As `A`, flip a different public repo `A/proj2` to private via Settings → Danger Zone → "Make this repository private" (which calls `repo_service.MakeRepoPrivate`). Verify `B`'s subscription list no longer contains `A/proj2`.

The asymmetry of outcomes between steps 4 and 5 — for the same state transition — is the gap.

## Direct Evidence (no PoC needed)

```
$ gh api repos/go-gitea/gitea/contents/services/repository/repository.go \
    --jq .content | base64 -d | grep -n "ClearRepoWatches\|ClearRepoStars" 

154:                  if err = repo_model.ClearRepoStars(ctx, repo.ID); err != nil {
157:                  if err = repo_model.ClearRepoWatches(ctx, repo.ID); err != nil {  # MakeRepoPrivate
273:                  if err = repo_model.ClearRepoStars(ctx, repo.ID); err != nil {  # updateRepository — ClearRepoWatches missing here
```

The fix-author's own test file confirms the asymmetry:

```
$ gh api repos/go-gitea/gitea/contents/services/repository/repository_test.go --jq .content | base64 -d | grep -n "Test.*VisibilityChanged\|Test.*ClearsWatches"

44:func TestUpdateRepositoryVisibilityChanged(t *testing.T) {     # only checks act.IsPrivate
73:func TestMakeRepoPrivateClearsWatches(t *testing.T) {           # checks watches are cleared
```

`TestUpdateRepositoryVisibilityChanged` explicitly calls `updateRepository(ctx, repo, true)` (line 53) and asserts `act.IsPrivate` (line 61) — but never verifies `GetRepoWatchersIDs` returns empty, while the parallel `TestMakeRepoPrivateClearsWatches` does. The test asymmetry mirrors the fix asymmetry.

## Impact

- An organization that uses [terraform-gitea](https://github.com/go-gitea/terraform-provider-gitea) or any other REST-API-driven automation to flip repositories private (the canonical IaC pattern) hits `updateRepository`, not `MakeRepoPrivate`.
- An organization using the official Gitea SDK (`go-sdk`, `py-gitea`, etc.) or `curl` scripts to make repos private after an internal policy change hits the same path.
- Multi-tenant Gitea-as-a-service operators with API-driven repository-lifecycle endpoints are exposed.

Stale watch rows leak through `GET /user/subscriptions` (with the watcher's own credentials), `GET /repos/{owner}/{repo}/subscribers` (stale `NumWatches` total), and become a re-leak surface for any future notification path that forgets the send-time access check.

## Suggested Fix

Drop-in mirror of the call already present in `MakeRepoPrivate`. In `services/repository/repository.go::updateRepository`, inside the existing `if repo.IsPrivate { ... }` branch (around line 265-276), add the `ClearRepoWatches` call directly after `ClearRepoStars`:

```go
// services/repository/repository.go
func updateRepository(ctx context.Context, repo *repo_model.Repository, visibilityChanged bool) (err error) {
    ...
    if visibilityChanged {
        ...
        // If repo has become private, we need to set its actions to private.
        if repo.IsPrivate {
            _, err = e.Where("repo_id = ?", repo.ID).Cols("is_private").Update(&activities_model.Action{
                IsPrivate: true,
            })
            if err != nil {
                return err
            }

            if err = repo_model.ClearRepoStars(ctx, repo.ID); err != nil {
                return err
            }

            // Match MakeRepoPrivate's behavior — see PR #36319 / GHSA-8fwc-qjw5-rvgp.
            // Stale watch rows on a now-private repo leak repository metadata to ex-watchers
            // via GET /user/subscriptions?private=true and through any future notification
            // path that does not have a send-time access check.
            if err = repo_model.ClearRepoWatches(ctx, repo.ID); err != nil {
                return err
            }
        }
        ...
    }
    ...
}
```

Regression test (mirror of `TestMakeRepoPrivateClearsWatches`) to add to `services/repository/repository_test.go`:

```go
func TestUpdateRepositoryClearsWatchesOnVisibilityChange(t *testing.T) {
    assert.NoError(t, unittest.PrepareTestDatabase())

    repo := unittest.AssertExistsAndLoadBean(t, &repo_model.Repository{ID: 1})
    assert.False(t, repo.IsPrivate)

    watchers, err := repo_model.GetRepoWatchersIDs(t.Context(), repo.ID)
    require.NoError(t, err)
    require.NotEmpty(t, watchers)

    repo.IsPrivate = true
    assert.NoError(t, updateRepository(t.Context(), repo, true))

    watchers, err = repo_model.GetRepoWatchersIDs(t.Context(), repo.ID)
    assert.NoError(t, err)
    assert.Empty(t, watchers)

    updatedRepo := unittest.AssertExistsAndLoadBean(t, &repo_model.Repository{ID: repo.ID})
    assert.Zero(t, updatedRepo.NumWatches)
}
```

Optional belt-and-suspenders: an integration test against `PATCH /api/v1/repos/{owner}/{repo}` with body `{"private": true}` that exercises the entire API path through `routers/api/v1/repo/repo.go::Edit`.

## Discovery Methodology

This finding follows the "sister-fix-incomplete" lens that has been productive across several recent reports: pick a recent advisory where the fix lands as a single PR touching one function, then grep the codebase for parallel call sites that should have received the same defense.

For Gitea:

1. Enumerate recent advisories via `gh api graphql ... securityVulnerabilities(ecosystem: GO, package: code.gitea.io/gitea)`.
2. GHSA-8fwc-qjw5-rvgp stood out because the description names a state transition (public→private) — a class of bug where the defense is typically wired into a single helper.
3. `gh api repos/.../commits/8a98ac221 --jq '.files[] | .filename'` listed the fix files; `ClearRepoWatches` was added to one function.
4. `grep -rn "ClearRepoWatches\|MakeRepoPrivate"` revealed two functions in `services/repository/repository.go` that handle the state transition: `MakeRepoPrivate` (patched) and the lowercase sister `updateRepository` (unpatched).
5. Walked the call chain from `routers/api/v1/repo/repo.go::Edit` to confirm the API path uses `updateRepository`, not `MakeRepoPrivate`.

## Pre-emptive rebuttals

- "The send-time filter in `MailNewRelease` already blocks release-content disclosure" — Correct, and acknowledged. The residual leak this report concerns is metadata via the `GET /user/subscriptions` endpoint and stale `NumWatches`. The send-time filter is a necessary but not sufficient defense; the `ClearRepoWatches` call is the persistence-side belt-and-suspenders that the original PR author explicitly added.
- "The web UI is the supported path; the API path is not in scope" — The API is documented public surface (swagger spec in `templates/swagger/v1_json.tmpl`), Gitea ships official SDKs (`go-sdk`, `py-gitea`) that use exactly this path, and there is an official Terraform provider that exercises it. The existing fix is in a sister helper used by both paths' upstream helper — the fix author plainly intended to defend both.
- "AccessMode is `None` in the subscription response, so the client should infer no-access" — The response still returns the full `Repository` payload including description, default branch, language, fork status, counts, mirror metadata, OriginalURL, license, etc. (see `services/convert/repository.go::innerToRepo` line 189-259). `AccessMode: 0` does not gate the metadata fields, only the `Permissions{Admin,Push,Pull}` triple.

## References

- GHSA-8fwc-qjw5-rvgp — the original advisory: https://github.com/go-gitea/gitea/security/advisories/GHSA-8fwc-qjw5-rvgp
- PR #36319 "clean watches when make a repository private and check permission when send release emails" (commit `8a98ac221`)
- PR #36959 "Require additional user confirmation for making repo private" (commit `943ff7523`) — the later refactor that did not propagate the cleanup
- Patched function: `services/repository/repository.go::MakeRepoPrivate` (line 125, calls `ClearRepoWatches` line 157)
- Unpatched sister: `services/repository/repository.go::updateRepository` (line 240, calls only `ClearRepoStars` line 273)
- API entry: `routers/api/v1/repo/repo.go::Edit` → `updateBasicProperties` → `repo_service.UpdateRepository` → `updateRepository`
- Test asymmetry: `services/repository/repository_test.go::TestMakeRepoPrivateClearsWatches` (covered) vs `TestUpdateRepositoryVisibilityChanged` (does not assert watches cleared)

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-q423-49rw-g9mh
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

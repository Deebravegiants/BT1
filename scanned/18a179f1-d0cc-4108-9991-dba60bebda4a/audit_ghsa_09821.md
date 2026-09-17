# [M] Vikunja: Scoped API tokens with projects.background permission can delete project backgrounds

## Summary
Severity: Medium
Advisory: GHSA-v479-vf79-mg83
CVE: CVE-2026-40103
CWE: CWE-836, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-v479-vf79-mg83
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
### Summary

Vikunja's scoped API token enforcement for custom project background routes is method-confused. A token with only `projects.background` can successfully delete a project background, while a token with only `projects.background_delete` is rejected.

This is a scoped-token authorization bypass.

### Details

I verified this locally on commit `c5450fb55f5192508638cbb3a6956438452a712e`.

Relevant code paths:
* `pkg/models/api_routes.go`
* `pkg/routes/routes.go`
* `pkg/modules/background/handler/background.go`

Route registration exposes separate permissions for the same path:
* `GET /api/v1/projects/:project/background` -> `projects.background`
* `DELETE /api/v1/projects/:project/background` -> `projects.background_delete`

At enforcement time, `CanDoAPIRoute()` falls back to the parent group and reconstructs the child permission from the path segments only. For the DELETE request, that becomes `background`, so the matcher accepts any token containing `projects.background` without re-checking the HTTP method or matching the stored route detail.

This matters because `RemoveProjectBackground()` is a real destructive operation:
* It checks project update rights.
* It deletes the background file if present.
* It clears the project's `BackgroundFileID`.

### PoC

1. Log in as a user who can update a project that already has a background.
2. Create an API token with only:
   `{"projects":["background"]}`
3. Send:
   `DELETE /api/v1/projects/<project_id>/background`
   `Authorization: Bearer <token>`
4. Observe that the request succeeds and the project background is removed.

**For comparison:**
1. Create an API token with only:
   `{"projects":["background_delete"]}`
2. Repeat the same DELETE request.
3. Observe that the request is rejected with `401 Unauthorized`.

I confirmed this locally with three validations:
1. `/api/v1/routes` advertises both `background` and `background_delete`.
2. The matcher unit test proves `CanDoAPIRoute()` accepts DELETE for `background`.
3. The webtest proves a real API token with only `background` successfully deletes the background.

### Impact

Scoped API tokens can exceed their intended capability. A token intended for project background access can delete project backgrounds, which weakens the trust model for automation and third-party integrations that rely on narrowly scoped tokens.

The attacker needs a valid API token created by a user who has update rights on the target project, but the token itself only needs the weaker `projects.background` permission.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-v479-vf79-mg83
- https://nvd.nist.gov/vuln/detail/CVE-2026-40103
- https://github.com/go-vikunja/vikunja/pull/2584
- https://github.com/go-vikunja/vikunja/commit/6a0f39b252a81fa4b19dc56dc889183acc9225ae
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0

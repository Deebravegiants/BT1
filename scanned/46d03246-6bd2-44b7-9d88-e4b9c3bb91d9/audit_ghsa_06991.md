# [M] Gitea: Cross-repository issue/comment attachment re-linking can expose private attachment content

## Summary
Severity: Medium
Advisory: GHSA-6c6r-5xr4-cr5m
CVE: CVE-2026-57886
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-6c6r-5xr4-cr5m
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

Gitea's issue and comment attachment update paths accept attachment UUIDs without verifying that each attachment belongs to the target issue/comment repository. If an authenticated attacker knows a victim attachment UUID, they can re-link that attachment to an attacker-controlled issue or comment, causing later attachment access checks to use the attacker's repository authorization context.

## Affected

- Component: web issue/comment attachment handling.
- Confirmed version: `main` commit `a39b2775edcb3ba53def96794491b91335117d81` (`v1.27.0-dev-352-ga39b2775ed`).
- Fixed in: not fixed at the time of validation.
- Other versions: not exhaustively tested. The affected code path appears structurally similar to versions that contain the current issue/comment attachment update logic.

## Description / Root Cause

`files[]` values from issue/comment edit flows are passed to `updateAttachments` in `routers/web/repo/issue.go:589-629`. That helper calls:

- `models/issues/issue_update.go:267-278` (`UpdateIssueAttachments`)
- `models/issues/comment.go:623-642` (`UpdateCommentAttachments`)

Both functions load attachments by UUID and update the attachment linkage, but neither validates that the attachment row's `RepoID` matches the repository of the target issue/comment. They also do not reject attachments already linked to a different issue/comment.

Attachment reads then use the linked issue/release repository to decide access:

- `services/repository/repository.go:185-207` returns the repository ID from `IssueID` or `ReleaseID`.
- `routers/web/repo/attachment.go:153-184` checks read permission on that linked repository.
- `routers/web/repo/attachment.go:216-224` opens and serves the file from the attachment's storage path after the linked-repository permission check succeeds.

For the global `/attachments/{uuid}` route in `routers/web/web.go:872-876`, there is no current repository context, so the early `attach.RepoID` mismatch check in `ServeAttachment` does not protect against this re-linking case.

A patched sibling path already demonstrates the intended invariant: `models/repo/release.go:179-215` rejects release attachments whose `RepoID` differs from the release repository. That guard was introduced for CVE-2026-20736, but the issue/comment paths still lack an equivalent check.

## Impact

An attacker who can edit an issue/comment in a repository they can read can move a known victim attachment UUID into that repository's authorization context. After the re-link, the attachment download path resolves access against the attacker-controlled repository while serving the original attachment file.

This can disclose private issue/comment attachments if the attacker has obtained the UUID through prior legitimate access, copied links, notification content, logs, browser history, or another exposure. The attack does not require write access to the victim repository.

## Reproduction Summary

Full HTTP/E2E observation:

- A local Gitea server was started with an isolated SQLite database.
- A victim user created private repositories, private issues, and issue attachments containing unique marker strings.
- An attacker user first attempted to download each victim attachment through `/attachments/{uuid}` and received `404`.
- The attacker then submitted the victim UUID through the real issue edit route in an attacker-controlled public repository.
- The same attacker could then download the victim issue attachment through `/attachments/{uuid}` and received `200`; the response body contained the unique issue marker.
- The attacker repeated the flow through the real comment edit route and could download the second victim attachment with `200`; the response body contained the unique comment marker.

Model-level issue-path behavior:

- A fixture attachment with `RepoID = 2` and `IssueID = 4` was passed to `UpdateIssueAttachments` for attacker issue `ID = 1`, whose `RepoID = 1`.
- The call succeeded.
- The attachment row still had `RepoID = 2`, but its `IssueID` was changed to the attacker issue.
- `GetAttachmentLinkedTypeAndRepoID` then resolved the attachment to attacker repository `RepoID = 1`.

Model-level comment-path behavior:

- The same cross-repository attachment UUID was passed to `UpdateCommentAttachments` for attacker comment `ID = 1`.
- The call succeeded.
- The attachment row still had `RepoID = 2`, but its `IssueID` and `CommentID` were changed to the attacker's issue/comment.
- The linked repository used for access checks became attacker repository `RepoID = 1`.

Negative control:

- Existing release test `TestAddReleaseAttachmentsRejectsDifferentRepo` passes and confirms the release path rejects the same class of cross-repository attachment linkage.

Detailed verifier and step-by-step runbook are available on request.

## Suggested Fix

Add repository and linkage validation before updating issue/comment attachments.

Recommended checks:

- Load the target issue for `UpdateIssueAttachments` and derive its `RepoID`.
- Load the target comment's issue for `UpdateCommentAttachments` and derive its `RepoID`.
- Reject any attachment whose `RepoID` differs from the target issue repository.
- Reject attachments already linked to a different issue/comment/release, except for attachments already linked to the same object being updated.
- If caller context is available at the web/service layer, also require new unlinked attachments to belong to the current actor or to have been uploaded in the current edit session.
- Preserve any legacy `RepoID = 0` migration behavior only when it can be proven safe for the target repository.

Also consider a cleanup/audit query for existing inconsistent rows where `attachment.issue_id != 0` and `attachment.repo_id` differs from the linked issue repository.

## Regression Tests

Add tests that fail before the fix and pass after it:

- `UpdateIssueAttachments` rejects an attachment whose `RepoID` differs from the target issue's `RepoID`.
- `UpdateCommentAttachments` rejects an attachment whose `RepoID` differs from the target comment issue's `RepoID`.
- Same-repository unlinked attachment linking still works for normal issue/comment editing.
- Attachments already linked to a different issue/comment cannot be moved by passing their UUID in `files[]`.
- Existing release guard test remains passing.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-6c6r-5xr4-cr5m
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

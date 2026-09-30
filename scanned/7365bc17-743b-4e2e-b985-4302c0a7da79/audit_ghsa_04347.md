# [H] praisonai-platform: Comment endpoints accept any issue_id without workspace ownership check, cross-workspace comment read and post IDOR

## Summary
Severity: High
Advisory: GHSA-cp4f-5m9r-5jc2
CVE: CVE-2026-47417
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-cp4f-5m9r-5jc2
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure Direct Object Reference. The comment endpoints (`POST /workspaces/{workspace_id}/issues/{issue_id}/comments` and `GET .../comments`) gate access on `require_workspace_member(workspace_id)` only, then call `CommentService.create(issue_id=issue_id, ...)` and `CommentService.list_for_issue(issue_id)` without verifying that `issue_id` belongs to `workspace_id`. A user who is a member of any workspace `W1` can read every comment on, and post new comments to, any issue in any other workspace `W2`.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/issues.py`, lines 143-171; `src/praisonai-platform/praisonai_platform/services/comment_service.py`, lines 19-53.
**Root cause:** the route extracts `workspace_id` from the URL path and uses it solely for the membership gate, then passes the URL-supplied `issue_id` straight into `CommentService` without confirming that this issue exists in `workspace_id`. `CommentService.list_for_issue(issue_id)` runs `SELECT * FROM comments WHERE issue_id = :issue_id` with no workspace join. `CommentService.create(issue_id=issue_id, ...)` blindly writes a row with that `issue_id`. Both flows trust the URL-supplied issue ID as authoritative even though the membership check guarantees nothing about it.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/api/routes/issues.py`, lines 143-171.

```python
@router.post("/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    workspace_id: str,
    issue_id: str,
    body: CommentCreate,
    user: AuthIdentity = Depends(require_workspace_member),         # only checks attacker is in workspace_id
    session: AsyncSession = Depends(get_db),
):
    svc = CommentService(session)
    comment = await svc.create(
        issue_id=issue_id,                                          # <-- BUG: no validation that issue_id is in workspace_id
        author_id=user.id,
        content=body.content,
        author_type="member" if user.is_user else "agent",
        parent_id=body.parent_id,
    )
    return CommentResponse.model_validate(comment)


@router.get("/{issue_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    workspace_id: str,
    issue_id: str,
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = CommentService(session)
    comments = await svc.list_for_issue(issue_id)                   # <-- BUG: returns comments on any issue
    return [CommentResponse.model_validate(c) for c in comments]
```

**File 2:** `src/praisonai-platform/praisonai_platform/services/comment_service.py`, lines 19-53.

```python
class CommentService:
    ...

    async def create(
        self,
        issue_id: str,
        author_id: str,
        content: str,
        author_type: str = "member",
        comment_type: str = "comment",
        parent_id: Optional[str] = None,
    ) -> Comment:
        comment = Comment(
            issue_id=issue_id,                                      # <-- accepts any issue_id; no workspace verify
            author_type=author_type,
            author_id=author_id,
            ...
        )
        self._session.add(comment)
        await self._session.flush()
        return comment

    async def list_for_issue(self, issue_id: str) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.issue_id == issue_id)                    # <-- no JOIN against issues for workspace constraint
            .order_by(Comment.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
```

**Why it's wrong:** the service trusts the caller-supplied `issue_id` as authoritative, but the route layer never verified that this issue belongs to the workspace the membership check covers. The standard FastAPI/SQLAlchemy fix is to first resolve the issue scoped to `workspace_id` (`Issue.id = :issue_id AND Issue.workspace_id = :workspace_id`) and only then proceed to comment operations. The `MemberService.get(workspace_id, user_id)` and `LabelService.list_for_workspace(workspace_id)` calls in the same codebase show the safe predicate; the comment service forgot to apply it.

## Exploit Chain

1. Attacker registers a workspace `W_attacker` (member) and harvests a target issue UUID `I_T` from any side channel: agent prompts that mention issues, the activity feed (`act_svc.log` records `issue_id`), webhook payloads, exported issue dumps, or simply by being a low-privilege observer of the attacker's own workspace whose internals reference foreign issue IDs (cross-workspace links, search across activity events). State: attacker holds `I_T`.
2. Attacker authenticates and sends `GET /workspaces/W_attacker/issues/I_T/comments`. `require_workspace_member(W_attacker, attacker)` passes (attacker is a member of `W_attacker`). State: control flow enters `list_comments` with `workspace_id=W_attacker, issue_id=I_T`.
3. `CommentService.list_for_issue(I_T)` runs `SELECT * FROM comments WHERE issue_id = 'I_T'` with no workspace constraint. Every comment on the foreign issue is returned: `content` (often the most sensitive part of an issue tracker — bug-report repro steps with secrets, customer PII, internal triage notes), `author_id`, `author_type`, `parent_id`, `created_at`. State: response body is the full comment thread of the foreign issue.
4. Attacker repeats with `POST /workspaces/W_attacker/issues/I_T/comments` and a body of `{"content": "<malicious>"}`. `CommentService.create(issue_id=I_T, author_id=attacker, ...)` writes a row with the foreign issue's id and the attacker's `author_id`. State: a new comment authored by the attacker appears in the foreign workspace's issue thread, indistinguishable to the foreign workspace's UI from a legitimate cross-workspace mention. Used at scale this becomes a comment-spam / phishing primitive (links in the comment body) targeting another tenant's users.
5. Final state: any attacker with one workspace-member token can exfiltrate every comment in the multi-tenant deployment given the issue UUIDs, and inject arbitrary comments under their own author identity into any foreign issue. The cross-workspace attribution gap is the worst part: the comment is recorded with the attacker's `author_id`, but the foreign workspace has no member with that id and the foreign workspace's audit logs show no event (the `act_svc.log` call in `add_comment` is omitted).

## Security Impact

**Severity:** sec-high. CVSS 7.6: network attack, low complexity, low privileges, no user interaction, scope unchanged, high confidentiality (full comment threads), high integrity (cross-workspace comment injection under attacker's own id), no availability claim.
**Attacker capability:** read every comment on every issue in the multi-tenant deployment given the issue UUIDs; post arbitrary comments under the attacker's identity into any foreign issue, allowing comment-spam, phishing-link injection into another tenant's UI, or social-engineering attribution attacks (the foreign workspace's UI renders a comment whose author belongs to no member of that workspace).
**Preconditions:** `praisonai-platform` is deployed multi-tenant; the attacker has any membership token; the target issue's UUID is known or guessable.
**Differential:** source-inspection-verified end-to-end. The asymmetry between `CommentService.list_for_issue(issue_id)` (no workspace predicate) and `LabelService.list_for_workspace(workspace_id)` (correctly workspace-scoped) confirms the gap. With the suggested fix below, every comment route first resolves the issue scoped to `workspace_id`, returns 404 if the issue is foreign, and only then proceeds.

## Suggested Fix

Resolve the issue scoped to `workspace_id` at the route layer before dispatching to `CommentService`. This both fixes the read and the write paths and avoids changing the `CommentService` signature.

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/issues.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/issues.py
@@ -141,6 +141,11 @@ async def delete_issue(...):
 # ── Comments ─────────────────────────────────────────────────────────────────


+async def _require_issue_in_workspace(session, workspace_id: str, issue_id: str):
+    issue = await IssueService(session).get(workspace_id, issue_id)  # workspace-scoped get (see companion advisory)
+    if issue is None:
+        raise HTTPException(status_code=404, detail="Issue not found")
+
 @router.post("/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
 async def add_comment(
     workspace_id: str,
@@ -149,6 +154,7 @@ async def add_comment(
     user: AuthIdentity = Depends(require_workspace_member),
     session: AsyncSession = Depends(get_db),
 ):
+    await _require_issue_in_workspace(session, workspace_id, issue_id)
     svc = CommentService(session)
     comment = await svc.create(
         issue_id=issue_id,
@@ -167,5 +173,6 @@ async def list_comments(
     user: AuthIdentity = Depends(require_workspace_member),
     session: AsyncSession = Depends(get_db),
 ):
+    await _require_issue_in_workspace(session, workspace_id, issue_id)
     svc = CommentService(session)
     comments = await svc.list_for_issue(issue_id)
```

Companion advisories file the same workspace-scoping gap for `AgentService`, `IssueService`, `ProjectService`, and `LabelService`. Each is a separate exploitable IDOR.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-cp4f-5m9r-5jc2
- https://github.com/MervinPraison/PraisonAI

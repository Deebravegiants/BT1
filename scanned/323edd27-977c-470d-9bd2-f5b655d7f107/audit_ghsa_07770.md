# [H] Gogs has a Protected Branch Deletion Bypass in Web Interface

## Summary
Severity: High
Advisory: GHSA-2c6v-8r3v-gh6p
CVE: CVE-2026-25232
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-2c6v-8r3v-gh6p
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.1

## Details
## Summary

An access control bypass vulnerability in Gogs web interface allows any repository collaborator with Write permissions to delete protected branches (including the default branch) by sending a direct POST request, completely bypassing the branch protection mechanism. This vulnerability enables privilege escalation from Write to Admin level, allowing low-privilege users to perform dangerous operations that should be restricted to administrators only.

Although Git Hook layer correctly prevents protected branch deletion via SSH push, the web interface deletion operation does not trigger Git Hooks, resulting in complete bypass of protection mechanisms.

## Details

### Affected Component

- **File**: `internal/route/repo/branch.go`
- **Function**: `DeleteBranchPost` (lines 110-155)
- **Route Configuration**: `internal/cmd/web.go:589`
  ```go
  m.Post("/delete/*", reqSignIn, reqRepoWriter, repo.DeleteBranchPost)
  ```

### Root Cause

The `DeleteBranchPost` function performs the following checks when deleting a branch:
1. ✅ User authentication (`reqSignIn`)
2. ✅ Write permission check (`reqRepoWriter`)
3. ✅ Branch existence verification
4. ✅ CommitID matching (optional parameter)
5. ❌ **Missing protected branch check**
6. ❌ **Missing default branch check**

While the UI layer (`internal/route/repo/issue.go:646-658`) correctly checks protected branch status and hides the delete button, attackers can directly construct POST requests to bypass UI restrictions.

### Vulnerable Code

**Vulnerable implementation** (`internal/route/repo/branch.go:110-155`):

```110:155:internal/route/repo/branch.go
func DeleteBranchPost(c *context.Context) {
	branchName := c.Params("*")
	commitID := c.Query("commit")

	defer func() {
		redirectTo := c.Query("redirect_to")
		if !tool.IsSameSiteURLPath(redirectTo) {
			redirectTo = c.Repo.RepoLink
		}
		c.Redirect(redirectTo)
	}()

	if !c.Repo.GitRepo.HasBranch(branchName) {
		return
	}
	if len(commitID) > 0 {
		branchCommitID, err := c.Repo.GitRepo.BranchCommitID(branchName)
		if err != nil {
			log.Error("Failed to get commit ID of branch %q: %v", branchName, err)
			return
		}

		if branchCommitID != commitID {
			c.Flash.Error(c.Tr("repo.pulls.delete_branch_has_new_commits"))
			return
		}
	}

	// 🔴 Vulnerability: Missing protected branch check here
	// Should add check like:
	// protectBranch, err := database.GetProtectBranchOfRepoByName(c.Repo.Repository.ID, branchName)
	// if protectBranch != nil && protectBranch.Protected { ... }

	if err := c.Repo.GitRepo.DeleteBranch(branchName, git.DeleteBranchOptions{
		Force: true,
	}); err != nil {
		log.Error("Failed to delete branch %q: %v", branchName, err)
		return
	}

	if err := database.PrepareWebhooks(c.Repo.Repository, database.HookEventTypeDelete, &api.DeletePayload{
		Ref:        branchName,
		RefType:    "branch",
		PusherType: api.PUSHER_TYPE_USER,
		Repo:       c.Repo.Repository.APIFormatLegacy(nil),
		Sender:     c.User.APIFormat(),
	}); err != nil {
		log.Error("Failed to prepare webhooks for %q: %v", database.HookEventTypeDelete, err)
		return
	}
}
```

**Correct implementation in Git Hook** (`internal/cmd/hook.go:122-125`):

```go
// check and deletion
if newCommitID == git.EmptyID {
    fail(fmt.Sprintf("Branch '%s' is protected from deletion", branchName), "")
}
```

**Correct UI layer check** (`internal/route/repo/issue.go:646-658`):

```go
protectBranch, err := database.GetProtectBranchOfRepoByName(pull.BaseRepoID, pull.HeadBranch)
if err != nil {
	if !database.IsErrBranchNotExist(err) {
		c.Error(err, "get protect branch of repository by name")
		return
	}
} else {
	branchProtected = protectBranch.Protected
}

c.Data["IsPullBranchDeletable"] = pull.BaseRepoID == pull.HeadRepoID &&
	c.Repo.IsWriter() && c.Repo.GitRepo.HasBranch(pull.HeadBranch) &&
	!branchProtected  // UI layer has check, but backend doesn't
```
## PoC

### Prerequisites

1. Have Write permissions to the target repository (collaborator or team member)
2. Target repository has protected branches configured (e.g., main, master, develop)
3. Access to Gogs web interface

#### Send Malicious POST Request
```bash
# Directly send DELETE request bypassing UI protection
curl -X POST \
  -b cookies.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "_csrf=YOUR_CSRF_TOKEN" \
  "https://gogs.example.com/username/repo/branches/delete/main"
```
<img width="1218" height="518" alt="image" src="https://github.com/user-attachments/assets/745da7c3-6139-408c-9747-ccbe9ea8548f" />

## Impact
- **Bypass branch protection mechanism**: The core function of protected branches is to prevent deletion, and this vulnerability completely undermines this mechanism
- **Delete default branch**: Can cause repository to become inaccessible (git clone/pull failures)
- **Bypass code review**: After deleting protected branch, can push new branch bypassing Pull Request requirements
- **Privilege escalation**: Writer permission users can perform operations that should only be allowed for Admins

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-2c6v-8r3v-gh6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-25232
- https://github.com/gogs/gogs/pull/8124
- https://github.com/gogs/gogs/commit/7b7e38c88007a7c482dbf31efff896185fd9b79c
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.1

